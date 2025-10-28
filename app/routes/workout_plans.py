from flask import Blueprint, request, jsonify, session
from app.supabase_client import supabase
from datetime import datetime, timezone

workout_plans_bp = Blueprint("workout_plans", __name__)

# --------------------------------------------------------
# CREATE WORKOUT PLAN
# --------------------------------------------------------
@workout_plans_bp.route("", methods=["POST"])
def create_workout_plan():
    """Insert a new workout plan row into workout_plans table."""
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = session["user"]
    data = request.get_json()

    if not data.get("name") or not data.get("exercises"):
        return jsonify({"error": "Missing workout name or exercises"}), 400

    new_plan = {
        "user_id": user["id"],
        "plan_name": data["name"],
        "description": data.get("description"),
        "exercises": data["exercises"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = supabase.table("workout_plans").insert(new_plan).execute()

    if not result.data:
        return jsonify({"error": "Failed to create workout plan"}), 500

    return jsonify(result.data[0]), 201


# --------------------------------------------------------
# GET ALL WORKOUT PLANS
# --------------------------------------------------------
@workout_plans_bp.route("", methods=["GET"])
def get_all_plans():
    """Return all plans for the logged-in user."""
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = session["user"]
    result = (
        supabase.table("workout_plans")
        .select("*")
        .eq("user_id", user["id"])
        .order("created_at", desc=True)
        .execute()
    )

    return jsonify(result.data or []), 200


# --------------------------------------------------------
# GET SINGLE WORKOUT PLAN
# --------------------------------------------------------
@workout_plans_bp.route("/<int:plan_id>", methods=["GET"])
def get_workout_plan(plan_id):
    """Get one workout plan by numeric id."""
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = session["user"]
    result = (
        supabase.table("workout_plans")
        .select("*")
        .eq("user_id", user["id"])
        .eq("id", plan_id)
        .single()
        .execute()
    )

    if not result.data:
        return jsonify({"error": "Workout plan not found"}), 404

    return jsonify(result.data), 200


# --------------------------------------------------------
# UPDATE WORKOUT PLAN
# --------------------------------------------------------
@workout_plans_bp.route("/<int:plan_id>", methods=["PUT"])
def update_workout_plan(plan_id):
    """Update an existing workout plan."""
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = session["user"]
    data = request.get_json()

    updates = {}
    if "plan_name" in data:
        updates["plan_name"] = data["plan_name"]
    if "description" in data:
        updates["description"] = data["description"]
    if "exercises" in data:
        updates["exercises"] = data["exercises"]

    result = (
        supabase.table("workout_plans")
        .update(updates)
        .eq("user_id", user["id"])
        .eq("id", plan_id)
        .execute()
    )

    if not result.data:
        return jsonify({"error": "Workout plan not found"}), 404

    return jsonify(result.data[0]), 200


# --------------------------------------------------------
# DELETE WORKOUT PLAN
# --------------------------------------------------------
@workout_plans_bp.route("/<int:plan_id>", methods=["DELETE"])
def delete_workout_plan(plan_id):
    """Delete a workout plan by id."""
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = session["user"]

    result = (
        supabase.table("workout_plans")
        .delete()
        .eq("user_id", user["id"])
        .eq("id", plan_id)
        .execute()
    )

    if not result.data:
        return jsonify({"error": "Workout plan not found"}), 404

    return jsonify({"message": "Workout plan deleted"}), 200
