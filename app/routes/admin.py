from flask import Blueprint, jsonify, request, session
from app.supabase_client import supabase

admin_bp = Blueprint("admin", __name__)

# Middleware to check admin status
def require_admin():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session["user"]["id"]
    
    # Check if user is admin
    profile = supabase.table("user_profile").select("admin").eq("id", user_id).single().execute()
    
    if not profile.data or not profile.data.get("admin"):
        return jsonify({"error": "Forbidden - Admin access required"}), 403
    
    return None

# ----------------------------
# GET ALL USERS
# ----------------------------
@admin_bp.route("/users", methods=["GET"])
def get_all_users():
    """Get all users ordered by creation date (most recent first)"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        response = supabase.table("user_profile").select("*").order("created_at", desc=True).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------
# DELETE USER
# ----------------------------
@admin_bp.route("/users/<user_id>", methods=["DELETE"])
def delete_user_admin(user_id):
    """Delete a user by ID"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        # Delete from auth.users via Supabase Admin API
        # Note: This requires admin privileges
        response = supabase.table("user_profile").delete().eq("id", user_id).execute()
        
        if not response.data:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------
# GET ALL POSTS
# ----------------------------
@admin_bp.route("/posts", methods=["GET"])
def get_all_posts():
    """Get all posts ordered by creation date (most recent first)"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        response = supabase.table("Posts").select(
            "id, content, title, like_count, created_at, user_profile!Posts_user_id_fkey(username)"
        ).order("created_at", desc=True).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------
# DELETE POST
# ----------------------------
@admin_bp.route("/posts/<post_id>", methods=["DELETE"])
def delete_post_admin(post_id):
    """Delete a post by ID"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        response = supabase.table("Posts").delete().eq("id", post_id).execute()
        
        if not response.data:
            return jsonify({"error": "Post not found"}), 404
        
        return jsonify({"message": "Post deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------
# GET ALL WORKOUT PLANS
# ----------------------------
@admin_bp.route("/workout-plans", methods=["GET"])
def get_all_workout_plans():
    """Get all workout plans ordered by creation date (most recent first)"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        response = supabase.table("workout_plans").select(
            "*, user_profile!workout_plans_user_id_fkey(username)"
        ).order("created_at", desc=True).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------
# DELETE WORKOUT PLAN
# ----------------------------
@admin_bp.route("/workout-plans/<int:plan_id>", methods=["DELETE"])
def delete_workout_plan_admin(plan_id):
    """Delete a workout plan by ID"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        response = supabase.table("workout_plans").delete().eq("id", plan_id).execute()
        
        if not response.data:
            return jsonify({"error": "Workout plan not found"}), 404
        
        return jsonify({"message": "Workout plan deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500