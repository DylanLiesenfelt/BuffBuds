from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)

@api_bp.route('/status', methods=['GET'])
def status():
        return jsonify({'status':'API Active'}), 200


"""
Main API Routes

This file contains the primary routes/endpoints for the BuffBuds application,
handling core features such as workouts, exercises, user feeds, and other
non-authentication related functionalities.

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