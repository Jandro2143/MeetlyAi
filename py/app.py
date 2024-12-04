from flask import Flask, render_template
from booking_calendar import calendar as render_calendar, book  # Import calendar and booking functions
from user_creation import user_blueprint  # Import the blueprint
from config import Config
import os

# Initialize Flask app
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "../pages"),
    static_folder=os.path.join(BASE_DIR, "../static"),
)

# Apply the configuration to the app
app.config.from_object(Config)

# Register the user blueprint
app.register_blueprint(user_blueprint, url_prefix="/user")

# Routes for pages
@app.route("/")
def home():
    """Home route."""
    return "Welcome to MeetlyAI"

@app.route("/sign_in")
def sign_in():
    """Sign In page."""
    return render_template("sign_in.html")

@app.route("/sign_up")
def sign_up():
    """Sign Up page."""
    return render_template("sign_up.html")

@app.route("/calendar/<string:user_id>", methods=["GET"])
def calendar_page(user_id):
    """Calendar page for a specific user."""
    try:
        return render_calendar(user_id)  # Pass user_id to the calendar function
    except Exception as e:
        return {"error": f"Error rendering calendar: {str(e)}"}, 500

@app.route("/book", methods=["POST"])
def create_booking():
    """Create a new booking."""
    try:
        return book()
    except Exception as e:
        return {"error": f"Error creating booking: {str(e)}"}, 500

# Start the Flask app
if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    app.run(debug=debug_mode)
