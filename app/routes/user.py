from flask import Blueprint, jsonify, request, session
from app.supabase_client import supabase

# Blueprint for user routes
user_bp = Blueprint("user", __name__)

# ----------------------
# CRUD Routes
# ----------------------

@user_bp.route("/users", methods=["GET"])
def get_users():
    """
    Fetch All Users

    Retrieves all user profiles from the 'user_profile' table.
    Returns JSON response with list of users or error message.
    """

    try:
        response = supabase.table("user_profile").select("*").execute()
        return jsonify({"users": response.data})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/users/<string:username>", methods=["GET"])
def get_user(username):
    """
    Fetch User by Username

    Retrieves a user profile by username from the 'user_profile' table.
    Returns JSON response with user data or error message.
    """

    try:
        response = supabase.table("user_profile").select("*").eq("username", username).execute()

        if response.data:
            return jsonify({"user": response.data})
        
        return jsonify({"error": "User not found"}), 404
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/users/<string:username>", methods=["PUT"])
def update_user(username):

    """
    Update User Profile
    
    Updates the user profile for the logged-in user.
    Expects JSON payload with fields to update.
    Returns JSON response with updated user data or error message.
    """

    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user = session["user"]  # from auth login
    data = request.json

    try:
        response = supabase.table("user_profile").update({
            "username": data.get("username"), # type: ignore
            "user_bio": data.get("user_bio"), # type: ignore
            "updated_at": "now()"
        }).eq("id", user["id"]).execute()

        return jsonify({"updated": response.data}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/users/<string:username>", methods=["DELETE"])
def delete_user(username):
    """
    Delete User Account
    Deletes the user account for the logged-in user.
    Expects no additional data.
    Returns JSON response with deletion status or error message.
    """

    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = session["user"]

    try:
        response = supabase.table("user_profile").delete().eq("id", user["id"]).execute()
        session.clear()

        return jsonify({"deleted": response.count}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------
# Follower System
# ------------------

@user_bp.route("/follow/<string:username>", methods=["POST"])
def follow_user(username):
    """
    Follow a User

    Authenticated user sends a request to follow another user specified by username.
    - Checks if the user is logged in.
    - Finds the target user to follow by username.
    - Prevents following yourself.
    - Checks if already following to avoid duplicates.
    - Inserts a new follower relationship into the followers table.
    Returns success or error messages accordingly.
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    follower_id = session["user"]["id"]

    # find the user to follow by username
    target_res = supabase.table("user_profile").select("id").eq("username", username).single().execute()
    if not target_res.data:
        return jsonify({"error": "User not found"}), 404

    followed_id = target_res.data["id"]

    # prevent user from following themselves
    if followed_id == follower_id:
        return jsonify({"error": "Cannot follow yourself"}), 400

    # check if following
    exists_res = supabase.table("followers").select("*").eq("follower_id", follower_id).eq("followed_id", followed_id).execute()

    if exists_res.data:
        return jsonify({"message": "Already following"}), 200

    # insert the new follow record
    insert_res = supabase.table("followers").insert({
        "follower_id": follower_id,
        "followed_id": followed_id
    }).execute()

    if insert_res.error: # type: ignore
        return jsonify({"error": insert_res.error.message}), 500 # type: ignore

    return jsonify({"message": f"Started following {username}"}), 201


@user_bp.route("/unfollow/<string:username>", methods=["POST"])
def unfollow_user(username):
    """
    Unfollow a User

    Authenticated user sends a request to unfollow another user specified by username.
    - Checks if user is logged in.
    - Finds the target user to unfollow by username.
    - Deletes the follower relationship from the followers table if it exists.
    Returns success or error messages accordingly.
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    follower_id = session["user"]["id"]

    # find the user to unfollow by username
    target_res = supabase.table("user_profile").select("id").eq("username", username).single().execute()
    if not target_res.data:
        return jsonify({"error": "User not found"}), 404

    followed_id = target_res.data["id"]

    # remove the following status
    delete_res = supabase.table("followers").delete().eq("follower_id", follower_id).eq("followed_id", followed_id).execute()

    if delete_res.error: # type: ignore
        return jsonify({"error": delete_res.error.message}), 500 # type: ignore

    if delete_res.count == 0:
        # not following that user in the first place
        return jsonify({"message": "You were not following this user"}), 200

    return jsonify({"message": f"Unfollowed {username}"}), 200


@user_bp.route("/<string:username>/followers", methods=["GET"])
def get_followers(username):
    """
    Get Followers List

    Retrieves a list of usernames who follow the specified user.
    - Finds the user ID by username.
    - Queries the followers table for all follower_ids of this user.
    - Fetches the usernames of those followers from user_profile table.
    Returns the list of follower usernames.
    """
    # find the user ID by username
    target_res = supabase.table("user_profile").select("id").eq("username", username).single().execute()
    if not target_res.data:
        return jsonify({"error": "User not found"}), 404

    user_id = target_res.data["id"]

    # get follower IDs who follow this user
    followers_res = supabase.table("followers").select("follower_id").eq("followed_id", user_id).execute()

    follower_ids = [f["follower_id"] for f in followers_res.data]

    if not follower_ids:
        # no followers found
        return jsonify({"followers": []})

    # get usernames of all followers
    users_res = supabase.table("user_profile").select("username").in_("id", follower_ids).execute()

    followers = [u["username"] for u in users_res.data]

    return jsonify({"followers": followers})


@user_bp.route("/<string:username>/following", methods=["GET"])
def get_following(username):
    """
    Get Following List

    Retrieves a list of usernames the specified user is following.
    - Finds the user ID by username.
    - Queries the followers table for all followed_ids that this user follows.
    - Fetches the usernames of those followed users from user_profile table.
    Returns the list of followed usernames.
    """
    # find the user ID by username
    target_res = supabase.table("user_profile").select("id").eq("username", username).single().execute()
    if not target_res.data:
        return jsonify({"error": "User not found"}), 404

    user_id = target_res.data["id"]

    # get IDs of users that this user is following
    following_res = supabase.table("followers").select("followed_id").eq("follower_id", user_id).execute()

    followed_ids = [f["followed_id"] for f in following_res.data]

    if not followed_ids:
        # not following anyone
        return jsonify({"following": []})

    # get usernames of all followed users
    users_res = supabase.table("user_profile").select("username").in_("id", followed_ids).execute()

    following = [u["username"] for u in users_res.data]

    return jsonify({"following": following})

# ---------------------
# Likes Features
# ---------------------

@user_bp.route("/like/<string:username>", methods=["POST"])
def like_user(username):
    """
    Like a User

    Authenticated user sends a request to like another user specified by username.
    - Checks if the user is logged in.
    - Finds the target user to like by username.
    - Prevents liking yourself.
    - Checks if already liked to avoid duplicates.
    - Inserts a new like record into the user_likes table.
    Returns success or error messages accordingly.
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user"]["id"]

    # get the user to be liked
    target_res = supabase.table("user_profile").select("id").eq("username", username).single().execute()
    if not target_res.data:
        return jsonify({"error": "User not found"}), 404

    liked_user_id = target_res.data["id"]

    if liked_user_id == user_id:
        return jsonify({"error": "Cannot like yourself"}), 400

    # check if already liked
    exists_res = supabase.table("user_likes").select("*").eq("user_id", user_id).eq("liked_user_id", liked_user_id).execute()

    if exists_res.data:
        return jsonify({"message": "Already liked"}), 200

    # add to liked
    insert_res = supabase.table("user_likes").insert({
        "user_id": user_id,
        "liked_user_id": liked_user_id
    }).execute()

    if insert_res.error: # type: ignore
        return jsonify({"error": insert_res.error.message}), 500 # type: ignore

    return jsonify({"message": f"You liked {username}"}), 201


@user_bp.route("/unlike/<string:username>", methods=["POST"])
def unlike_user(username):
    """
    Unlike a User

    Authenticated user sends a request to unlike another user specified by username.
    - Checks if user is logged in.
    - Finds the target user to unlike by username.
    - Deletes the like record from the user_likes table if it exists.
    Returns success or error messages accordingly.
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user"]["id"]

    # get the user to be unliked
    target_res = supabase.table("user_profile").select("id").eq("username", username).single().execute()
    if not target_res.data:
        return jsonify({"error": "User not found"}), 404

    liked_user_id = target_res.data["id"]

    # delete the like
    delete_res = supabase.table("user_likes").delete().eq("user_id", user_id).eq("liked_user_id", liked_user_id).execute()

    if delete_res.error: # type: ignore
        return jsonify({"error": delete_res.error.message}), 500 # type: ignore

    if delete_res.count == 0:
        return jsonify({"message": "You had not liked this user"}), 200

    return jsonify({"message": f"You unliked {username}"}), 200


@user_bp.route("/<string:username>/likes", methods=["GET"])
def get_likes(username):
    """
    Get Likes List

    Retrieves a list of usernames who liked the specified user.
    - Finds the user ID by username.
    - Queries the user_likes table for all user_ids who liked this user.
    - Fetches the usernames of those users from user_profile table.
    Returns the list of usernames who liked the user.
    """
    # get user id
    target_res = supabase.table("user_profile").select("id").eq("username", username).single().execute()
    if not target_res.data:
        return jsonify({"error": "User not found"}), 404

    liked_user_id = target_res.data["id"]

    # find all users who liked this user
    likes_res = supabase.table("user_likes").select("user_id").eq("liked_user_id", liked_user_id).execute()

    liker_ids = [like["user_id"] for like in likes_res.data]

    if not liker_ids:
        return jsonify({"likes": []})

    # get usernames of those who liked
    users_res = supabase.table("user_profile").select("username").in_("id", liker_ids).execute()

    likers = [u["username"] for u in users_res.data]

    return jsonify({"likes": likers})

@user_bp.route("/volume-history", methods=["GET"])
def get_volume_history():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user"]["id"]

    response = supabase.table("user_profile") \
        .select("volume_history") \
        .eq("id", user_id) \
        .single() \
        .execute()

    # ----------------------------------------------------------------
    # FIX: SingleAPIResponse DOES NOT have .error — only .data exists
    # ----------------------------------------------------------------
    if response.data is None:
        return jsonify({"error": "No profile found"}), 404

    volume_history = response.data.get("volume_history", [])

    # Ensure JSON serializable datetime
    safe_history = []
    for item in volume_history:
        safe_history.append({
            "date": str(item["date"]),
            "volume": item["volume"]
        })

    return jsonify(safe_history), 200

