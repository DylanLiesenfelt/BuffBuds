from flask import Flask, jsonify, request
from client import supabase  # Import shared Supabase client

app = Flask(__name__)

# ----------------------------
# Test DB connection
# ----------------------------
@app.route('/test-db')
def test_db():
    try:
        response = supabase.table('User').select('*').execute()
        return {'status': 'success', 'data': response.data}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

# ----------------------------
# Fetch all users
# ----------------------------
@app.route('/users', methods=['GET'])
def get_users():
    try:
        response = supabase.table('User').select('*').execute()
        return jsonify({'users': response.data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----------------------------
# Fetch single user by email
# ----------------------------
@app.route('/users/<string:user_email>', methods=['GET'])
def get_user(user_email):
    try:
        response = supabase.table('User').select('*').eq('user_email', user_email).execute()
        if response.data:
            return jsonify({'user': response.data[0]})
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----------------------------
# Create new user
# ----------------------------
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    try:
        response = supabase.table('User').insert({
            'user_email': data.get('user_email'),
            'user_pass': data.get('user_pass')
        }).execute()
        return jsonify({'created': response.data}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----------------------------
# Update user password by email
# ----------------------------
@app.route('/users/<string:user_email>', methods=['PUT'])
def update_user(user_email):
    data = request.json
    try:
        response = supabase.table('User').update({
            'user_pass': data.get('user_pass')
        }).eq('user_email', user_email).execute()
        return jsonify({'updated': response.data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----------------------------
# Delete user by email
# ----------------------------
@app.route('/users/<string:user_email>', methods=['DELETE'])
def delete_user(user_email):
    try:
        response = supabase.table('User').delete().eq('user_email', user_email).execute()
        return jsonify({'deleted': response.count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
