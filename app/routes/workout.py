from flask import Blueprint, request, jsonify, session
from datetime import datetime
import uuid
from app.supabase_client import supabase

workouts_bp = Blueprint("workout", __name__)

# ----------------------------
# CREATE WORKOUT SESSION
# ----------------------------
@workouts_bp.route("/workouts", methods=["POST"])
def create_workout():
    """
    -  session is linked to the user's ID 
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = session["user"]
    data = request.get_json()

    # Creating a workout entry 
    workout = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],  # link to user_profile
        "session_date": data.get("session_date", datetime.utcnow().isoformat()),
        "exercise_name": data.get("exercise_name"),
        "num_reps": data.get("num_reps"),
        "num_sets": data.get("num_sets"),
        "exercise_weight": data.get("exercise_weight"),
        "notes": data.get("notes"),
    }

    response = supabase.table("workout_session").insert(workout).execute() # type: ignore
    return jsonify(response.data[0]), 201


# ----------------------------
# GET ALL WORKOUTS 
# ----------------------------
@workouts_bp.route("/workouts", methods=["GET"])
def get_workouts():
    """
    - Retrieve all workout sessions for the user
    - Orders them by session_date
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = session["user"]
    response = supabase.table("workout_session").select( # type: ignore
        "id, session_date, exercise_name, num_sets, num_reps, exercise_weight, notes"
    ).eq("user_id", user["id"]).order("session_date", desc=True).execute()

    return jsonify(response.data), 200


# ----------------------------
# GET WORKOUT BY DATE
# ----------------------------
@workouts_bp.route("/workouts/<date>", methods=["GET"])
def get_workout_by_date(date):
    """
    Retrieve all exercises logged on a specific date for the logged-in user.
    - Useful when viewing a specific workout day.
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = session["user"]
    response = supabase.table("workout_session").select(
        "id, session_date, exercise_name, num_sets, num_reps, exercise_weight, notes"
    ).eq("user_id", user["id"]).eq("session_date", date).execute()

    return jsonify(response.data), 200


# ----------------------------
# UPDATE WORKOUT SESSION
# ----------------------------
@workouts_bp.route("/workouts/<workout_id>", methods=["PUT"])
def update_workout(workout_id):
    """
    Update an existing workout entry.
    - Ensures only the owner can modify their data.
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = session["user"]
    data = request.get_json()

    response = supabase.table("workout_session").update({
        "exercise_name": data.get("exercise_name"),
        "num_reps": data.get("num_reps"),
        "num_sets": data.get("num_sets"),
        "exercise_weight": data.get("exercise_weight"),
        "notes": data.get("notes")
    }).eq("id", workout_id).eq("user_id", user["id"]).execute()

    if not response.data:
        return jsonify({"error": "Workout not found or unauthorized"}), 404

    return jsonify(response.data[0]), 200


# ----------------------------
# DELETE WORKOUT SESSION
# ----------------------------
@workouts_bp.route("/workouts/<workout_id>", methods=["DELETE"])
def delete_workout(workout_id):
    """
    Delete a workout entry.
    - checks that the workout belongs to the logged-in user.
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = session["user"]

    response = supabase.table("workout_session").delete().eq("id", workout_id).eq("user_id", user["id"]).execute()

    if not response.data:
        return jsonify({"error": "Workout not found or unauthorized"}), 404

    return jsonify({"message": "Workout has deleted successfully"}), 200
