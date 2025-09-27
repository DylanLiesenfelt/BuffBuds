from flask import Blueprint, jsonify, request, session
from app.supabase_client import supabase  

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods= ['POST'])
def login():

    """
    User Login Route

    Uses Supabase auth to sign in with email and password.
    On successful login, stores user info in session.
    Expects JSON payload with 'email' and 'password'.
    Returns JSON response with success or error message.
    """

    data = request.json
    email = data.get("email")
    password = data.get(("password"))

    if not email or not password:
        return jsonify({"error":"Email and Password are required"}),400
    
    try: 
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if res.user:
            # fetch username from user_profile
            profile = supabase.table("user_profile").select("username").eq("id", res.user.id).single().execute()
            username = profile.data["username"] if profile.data else None

            # store user info in session
            session["user"] = {
                "id": res.user.id,
                "email": res.user.email,
                "username": username
            }
            return jsonify({
                "message": "Login Successful",
                "user": session["user"]
            }), 200
        
        return jsonify({"error": "Email or Password Incorrect"}), 401
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/signup', methods=['POST'])
def signup():

    """
    User Signup Route

    Uses Supabase auth to create a new user with email and password.
    On successful signup, also creates a user profile in 'user_profile' table.
    Expects JSON payload with 'email', 'password', and 'username'.
    Returns JSON response with success or error message.
    """

    data = request.json
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    try:
        res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        if res.user:
            # INSERT to user_profile table
            supabase.table("user_profile").insert({
                "id": res.user.id,        
                "username": username,
                "created_at": "now()",
                "updated_at": "now()"
            }).execute()
            return jsonify({"message": "User created", "user": res.user.email}), 201
        
        return jsonify({"error": "Signup failed"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@auth_bp.route("/logout", methods=["POST"])
def logout():

    """
    User Logout Route

    Clears user session on logout.
    Expects no additional data.
    Returns JSON response with success or error message.
    """

    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    session.clear()
    return jsonify({"message": "Logged out"}), 200


@auth_bp.route("/status", methods=["GET"])
def status():
    user = session.get("user")
    if user:
        return jsonify({"authenticated": True, "user": user}), 200
    return jsonify({"authenticated": False}), 200


"""
Authentication Routes

This file contains routes related to user authentication and authorization,
including login, signup, logout, and possibly token refresh endpoints.

HTTP Methods for Flask Routes:

| Method  | Description                     | Use Case Example                     |
|---------|---------------------------------|------------------------------------|
| GET     | Retrieve or display data         | Show a webpage or fetch info       |
| POST    | Submit or create data            | Handle form submissions            |
| PUT     | Replace or update existing data  | Update a full resource             |
| PATCH   | Partially update existing data   | Update part of a resource          |
| DELETE  | Remove data                     | Delete a resource                  |

Notes:
- If 'methods' is not specified, Flask defaults to ['GET'].
- Specify 'methods' when your route needs to handle POST, PUT, DELETE, etc.
- When using address bar in browser for testing the route, GET is used
- http://127.0.0.1:5000/ + route (/api/ for main routes)

"""