# app/routes/posts.py
from flask import Blueprint, request, jsonify, session
from app.supabase_client import supabase
from datetime import datetime, timezone
import uuid

posts_bp = Blueprint("posts", __name__)

# ----------------------------
# CREATE POST
# ----------------------------
@posts_bp.route("/", methods=["POST"])
def create_post():
    """
    Create a new post.
    -user_id in posts table is a foreign key to user_profile table referencing user_id
    - Initializes like_count to 0 and comments as an empty list.
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = session["user"]  # user profile from login
    data = request.get_json()

    profile = supabase.table("user_profile").select("id").eq("id", user["id"]).single().execute()

    if not profile.data:
        return jsonify({"error": "User profile not found"}), 404

    post = {
        "user_id": profile.data["id"],
        "content": data.get("content"),
        "like_count": 0,
        "comments": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "title": data.get("title")
    }

    response = supabase.table("Posts").insert(post).execute()
    return jsonify(response.data[0]), 201


# ----------------------------
# READ POSTS
# ----------------------------
@posts_bp.route("/", methods=["GET"])
def get_posts():
    """
    Fetch all posts.
    """
    response = supabase.table("Posts").select(
        "id, content, like_count, comments, created_at, title, liked_by, user_profile!Posts_user_id_fkey(username)"   
    ).execute()
    return jsonify(response.data), 200


@posts_bp.route("/<post_id>", methods=["GET"])
def get_post(post_id):
    """
    Fetch a single post by ID.
    """
    response = supabase.table("Posts").select(
        "id, content, like_count, comments, created_at, title, liked_by, user_profile!Posts_user_id_fkey(username)"   
    ).eq("id", post_id).execute()
    if not response.data:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(response.data[0]), 200


# ----------------------------
# LIKE A POST
# ----------------------------
@posts_bp.route("/<post_id>/like", methods=["POST"])
def like_post(post_id):
    """
    Adds the current user's ID to liked_by and increments like_count.
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user"]["id"]

    post = supabase.table("Posts").select("like_count, liked_by").eq("id", post_id).single().execute()
    if not post.data:
        return jsonify({"error": "Post not found"}), 404

    liked_by = post.data.get("liked_by") or []
    like_count = post.data.get("like_count") or 0

    if user_id not in liked_by:
        liked_by.append(user_id)
        like_count += 1

        supabase.table("Posts").update({
            "like_count": like_count,
            "liked_by": liked_by
        }).eq("id", post_id).execute()

    return jsonify({"like_count": like_count, "liked_by": liked_by}), 200

# ----------------------------
# UNLIKE A POST
# ----------------------------
@posts_bp.route("/<post_id>/unlike", methods=["PUT"])
def unlike_post(post_id):
    """
    Removes the current user's ID from liked_by and decrements like_count.
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user"]["id"]

    post = supabase.table("Posts").select("like_count, liked_by").eq("id", post_id).single().execute()
    if not post.data:
        return jsonify({"error": "Post not found"}), 404

    liked_by = post.data.get("liked_by") or []
    like_count = post.data.get("like_count") or 0

    if user_id in liked_by:
        liked_by.remove(user_id)
        like_count = max(0, like_count - 1)

        supabase.table("Posts").update({
            "like_count": like_count,
            "liked_by": liked_by
        }).eq("id", post_id).execute()

    return jsonify({"like_count": like_count, "liked_by": liked_by}), 200

# ----------------------------
# ADD COMMENT
# ----------------------------
@posts_bp.route("/<post_id>/comment", methods=["POST"])
def comment_post(post_id):
    """
    Add a comment to a post.
    """
    if "user" not in session:
        return jsonify({"error": "User not logged in"}), 401

    data = request.get_json()
    comment_text = data.get("text")

    if not comment_text:
        return jsonify({"error": "Comment cannot be empty"}), 400

    # Get current user info
    user = session["user"]

    # Fetch the current post
    post_response = supabase.table("Posts").select("comments").eq("id", post_id).execute()

    if not post_response.data or len(post_response.data) == 0:
        return jsonify({"error": "Post not found"}), 404

    # Get the existing comments (if any)
    existing_comments = post_response.data[0].get("comments") or []

    # new comment
    new_comment = {
    "username": user.get("username", "unknown"),
    "text": comment_text,
    "created_at": datetime.now(timezone.utc).isoformat(),
}


    # Append the new comment to the list
    updated_comments = existing_comments + [new_comment]

    # Update Supabase
    update_response = (
        supabase.table("Posts")
        .update({"comments": updated_comments})
        .eq("id", post_id)
        .execute()
    )

    if update_response.data is None:
        return jsonify({"error": "Failed to update comments"}), 500

    return jsonify({"message": "Comment added successfully", "comment": new_comment}), 200




# ----------------------------
# GET COMMENTS FOR A POST
# ----------------------------
@posts_bp.route("/<post_id>/comments", methods=["GET"])
def get_comments(post_id):
    post = supabase.table("Posts").select("comments").eq("id", post_id).single().execute()
    if not post.data:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(post.data.get("comments", [])), 200


# ----------------------------
# COMMENT DELETION
# ----------------------------
@posts_bp.route("/<post_id>/comment/<int:comment_index>", methods=["DELETE"])
def delete_comment(post_id, comment_index):
    """
    Delete a specific comment from a post.
    Only the comment's author can delete it.
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = session["user"]
    data = request.get_json()

    comment = {
        "username": user["username"],
        "text": data.get("text"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    # Fetch the post's comments
    post = supabase.table("Posts").select("comments").eq("id", post_id).single().execute()
    if not post.data:
        return jsonify({"error": "Post not found"}), 404

    comments = post.data.get("comments", [])
    if comment_index < 0 or comment_index >= len(comments):
        return jsonify({"error": "Invalid comment index"}), 400

    # Only allow deletion if the current user is the comment author
    if comments[comment_index]["username"] != user["username"]:
        return jsonify({"error": "Unauthorized"}), 403

    # Remove the comment
    comments.pop(comment_index)

    # Update Supabase
    supabase.table("Posts").update({"comments": comments}).eq("id", post_id).execute()

    return jsonify({"message": "Comment deleted"}), 200



# ----------------------------
# UPDATE (EDIT) POST
# ----------------------------
@posts_bp.route("/<post_id>", methods=["PUT"])
def update_post(post_id):
    """
    Edit a post's content.
    - Only the owner can edit their post.
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = session["user"]
    data = request.get_json()

    # Fetch post owner
    post = supabase.table("Posts").select("user_id").eq("id", post_id).single().execute()
    if not post.data:
        return jsonify({"error": "Post not found"}), 404
    
    #using user_id for stricter check as usernme can be changed
    if post.data["user_id"] != user["id"]: 
        return jsonify({"error": "Unauthorized"}), 403

    # Only allow updating content
    updates = {}
    if "content" in data:
        updates["content"] = data["content"]

    response = supabase.table("Posts").update(updates).eq("id", post_id).execute()
    return jsonify(response.data[0]), 200


# ----------------------------
# DELETE POST
# ----------------------------
@posts_bp.route("/<post_id>", methods=["DELETE"])
def delete_post(post_id):
    """
    Delete a post.
    - Only the owner can delete their post.
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = session["user"]

    # Fetch post owner
    #using user_id for stricter check as usernme can be changed
    post = supabase.table("Posts").select("user_id").eq("id", post_id).single().execute()
    if not post.data:
        return jsonify({"error": "Post not found"}), 404

    if post.data["user_id"] != user["id"]:
        return jsonify({"error": "Unauthorized"}), 403

    supabase.table("Posts").delete().eq("id", post_id).execute()
    return jsonify({"message": "Post deleted successfully"}), 200

# ----------------------------
# GET POSTS FOR A USER
# ----------------------------
@posts_bp.route("/user/<username>", methods=["GET"])
def get_user_posts(username):
    """
    Fetch all posts created by a given user.
    Joins against user_profile to filter by username.
    """
    profile = (
        supabase.table("user_profile")
        .select("id")
        .eq("username", username)
        .single()
        .execute()
    )

    if not profile.data:
        return jsonify([]), 200

    user_id = profile.data["id"]

    response = (
        supabase.table("Posts")
        .select("id, content, like_count, comments, created_at, title, user_id")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return jsonify(response.data or []), 200