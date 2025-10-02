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
def update_user():

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
        response = supabase.table("UserProfile").update({
            "username": data.get("username"),
            "user_bio": data.get("user_bio"),
            "updated_at": "now()"
        }).eq("id", user["id"]).execute()

        return jsonify({"updated": response.data}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/users/<string:username>", methods=["DELETE"])
def delete_user():
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
        response = supabase.table("UserProfile").delete().eq("id", user["id"]).execute()
        session.clear()

        return jsonify({"deleted": response.count}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
