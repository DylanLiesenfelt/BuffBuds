from flask import Blueprint, jsonify, request, session
from app.supabase_client import supabase  

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods= ['POST'])
def login():
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
            # fetch username and admin status from user_profile
            profile = supabase.table("user_profile").select("username, admin").eq("id", res.user.id).single().execute()
            
            print("Profile data:", profile.data)  # Debug log
            
            username = profile.data["username"] if profile.data else None
            is_admin = profile.data.get("admin", False) if profile.data else False
            
            print(f"Username: {username}, is_admin: {is_admin}")  # Debug log

            # store user info in session
            session["user"] = {
                "id": res.user.id,
                "email": res.user.email,
                "username": username,
                "admin": is_admin  # NEW
            }
            
            print("Session user:", session["user"])  # Debug log
            
            return jsonify({
                "message": "Login Successful",
                "user": session["user"]
            }), 200
        
        return jsonify({"error": "Email or Password Incorrect"}), 401
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    try:
        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {"username": username}
            }
        })

        print("Signup response:", res)

        return jsonify({
            "message": "Signup successful. Please verify your email to activate your account.",
            "email": email
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@auth_bp.route("/logout", methods=["POST"])
def logout():
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

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    password = data.get("password")
    token = data.get("access_token")

    if not password or not token:
        return jsonify({"error": "Missing password or token"}), 400

    try:
        res = supabase.auth.api.update_user(token, {"password": password})
        if res.get("error"):
            return jsonify({"error": res["error"]["message"]}), 400
        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500