from flask import Blueprint, request, jsonify
from pyairtable import Table
import uuid
from config import Config  # Importing the Config class

# Blueprint for user routes
user_blueprint = Blueprint("user_creation", __name__)

def get_airtable_table(table_name):
    """Retrieve the Airtable table using the Config class."""
    airtable_api_key = Config.AIRTABLE_API_KEY
    base_id = Config.BASE_ID
    return Table(airtable_api_key, base_id, table_name)

@user_blueprint.route("/create_user", methods=["POST"])
def create_user():
    """Endpoint to create a new user."""
    try:
        # Airtable table setup
        table = get_airtable_table(Config.USERS_TABLE)  # Use USERS_TABLE from Config

        data = request.json  # Get the JSON payload

        # Validate required fields
        required_fields = ["first_name", "last_name", "email", "password"]
        if not all(field in data for field in required_fields):
            return jsonify({"message": "Missing required fields"}), 400

        # Generate a unique ID for the user
        unique_id = str(uuid.uuid4())

        # Prepare the user data
        user_data = {
            "First Name": data["first_name"],
            "Last Name": data["last_name"],
            "Email": data["email"],
            "Password": data["password"],  # Hash this in a production app
            "Unique ID": unique_id,
        }

        # Create the user in Airtable
        table.create(user_data)

        return jsonify({"message": "User created successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error creating user: {str(e)}"}), 500

@user_blueprint.route("/sign_in", methods=["POST"])
def sign_in():
    """Endpoint to authenticate a user."""
    try:
        # Airtable table setup
        table = get_airtable_table(Config.USERS_TABLE)

        data = request.json  # Get the JSON payload

        # Validate required fields
        required_fields = ["email", "password"]
        if not all(field in data for field in required_fields):
            return jsonify({"message": "Missing email or password"}), 400

        email = data["email"]
        password = data["password"]

        # Query Airtable for the user by email
        records = table.all(formula=f"{{Email}} = '{email}'")

        if not records:
            return jsonify({"message": "Invalid email or password"}), 401

        # Check the password
        user = records[0]["fields"]  # Get the first matched user
        if user.get("Password") != password:
            return jsonify({"message": "Invalid email or password"}), 401

        # Success - you can include more user details here if needed
        return jsonify({
            "message": "Sign-in successful!",
            "user": {
                "first_name": user.get("First Name"),
                "last_name": user.get("Last Name"),
                "email": user.get("Email"),
            }
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error during sign-in: {str(e)}"}), 500
