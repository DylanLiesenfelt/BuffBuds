# app/routes/posts.py
from flask import Blueprint, request, jsonify, session
from app.supabase_client import supabase
from datetime import datetime
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

    post = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],  # FK to user_profile (for stricter ownership checks)
        "content": data.get("content"),
        "like_count": 0,
        "comments": [],
        "created_at": datetime.now(datetime.timezone.utc).isoformat(),
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
        "id, content, like_count, comments, created_at, title, user_profile!Posts_user_id_fkey(username)"   
    ).execute()
    return jsonify(response.data), 200


@posts_bp.route("/<post_id>", methods=["GET"])
def get_post(post_id):
    """
    Fetch a single post by ID.
    """
    response = supabase.table("Posts").select(
        "id, content, like_count, comments, created_at, title, user_profile!Posts_user_id_fkey(username)"   
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
    Increment like_count for a post.
    - No user restriction, anyone can like.
    """
    post = supabase.table("Posts").select("like_count").eq("id", post_id).single().execute()
    if not post.data:
        return jsonify({"error": "Post not found"}), 404

    new_count = post.data["like_count"] + 1
    response = supabase.table("Posts").update({"like_count": new_count}).eq("id", post_id).execute()
    return jsonify(response.data[0]), 200


# ----------------------------
# ADD COMMENT
# ----------------------------
@posts_bp.route("/<post_id>/comment", methods=["POST"])
def add_comment(post_id):
    """
    Add a comment to a post.
    - Requires logged-in user.
    - Stores comments as JSONB array in Supabase.
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = session["user"]
    data = request.get_json()

    comment = {
        "username": user["username"],
        "text": data.get("text"),
        "created_at": datetime.now(datetime.timezone.utc).isoformat()
    }

    # Fetch existing comments
    post = supabase.table("Posts").select("comments").eq("id", post_id).single().execute()
    if not post.data:
        return jsonify({"error": "Post not found"}), 404

    comments = post.data["comments"] or []
    comments.append(comment)

    response = supabase.table("Posts").update({"comments": comments}).eq("id", post_id).execute()
    return jsonify(response.data[0]), 200


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
    response = supabase.table("Posts").select(
        "id, content, like_count, comments, created_at, title, user_profile!Posts_user_id_fkey(username)"
    ).eq("user_profile.username", username).execute()

    if not response.data:
        return jsonify([]), 200 

    return jsonify(response.data), 200