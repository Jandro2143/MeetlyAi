from flask import Flask, request
import requests
from dateutil import parser
import pytz

app = Flask(__name__)

# Constants
USER_API_URL = "https://info-54940.bubbleapps.io/version-test/api/1.1/obj/User"
BOOKING_API_URL = "https://info-54940.bubbleapps.io/version-test/api/1.1/obj/Booking"
API_KEY = "e58f0332d3bf9c0be92f50b2e1871c05"
LOCAL_TIMEZONE = pytz.timezone("Australia/Sydney")  # Adjust timezone as needed

@app.route("/")
def get_user_bookings():
    # Get the user_id from query parameters
    user_id = request.args.get("user_id")
    if not user_id:
        return {"error": "user_id is required to fetch bookings."}, 400

    # Step 1: Verify User exists
    user_response = requests.get(
        f"{USER_API_URL}?constraints=[{{\"key\":\"User ID\",\"constraint_type\":\"equals\",\"value\":\"{user_id}\"}}]",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    if user_response.status_code != 200 or not user_response.json()["response"]["results"]:
        return {"error": "User not found."}, 404

    # Step 2: Fetch Bookings for the User
    booking_response = requests.get(
        f"{BOOKING_API_URL}?constraints=[{{\"key\":\"User ID\",\"constraint_type\":\"equals\",\"value\":\"{user_id}\"}}]",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    if booking_response.status_code != 200:
        return {"error": f"Error fetching bookings: {booking_response.text}"}, booking_response.status_code

    try:
        bookings = booking_response.json()["response"]["results"]
        booked_slots = {}

        # Process bookings into day/time slots
        for booking in bookings:
            if "Date" in booking:
                booking_date = parser.isoparse(booking["Date"]).astimezone(LOCAL_TIMEZONE)
                day = booking_date.strftime("%Y-%m-%d")
                time = booking_date.strftime("%I:%M %p")
                if day not in booked_slots:
                    booked_slots[day] = []
                booked_slots[day].append(time)
    except Exception as e:
        return {"error": f"Error processing bookings: {str(e)}"}, 500

    return {"user_id": user_id, "booked_slots": booked_slots}, 200


@app.route("/book", methods=["POST"])
def create_booking():
    data = request.json

    # Validate required fields
    user_id = data.get("user_id")
    if not user_id:
        return {"error": "user_id is required to create a booking."}, 400

    # Step 1: Verify User exists
    user_response = requests.get(
        f"{USER_API_URL}?constraints=[{{\"key\":\"User ID\",\"constraint_type\":\"equals\",\"value\":\"{user_id}\"}}]",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    if user_response.status_code != 200 or not user_response.json()["response"]["results"]:
        return {"error": "User not found."}, 404

    try:
        # Combine date and time, convert to UTC
        local_datetime = f"{data['date']} {data['time']}"
        local_datetime_obj = parser.parse(local_datetime)
        utc_datetime = LOCAL_TIMEZONE.localize(local_datetime_obj).astimezone(pytz.utc)

        # Booking payload for Bubble
        booking_payload = {
            "Date": utc_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "First Name": data["first_name"],
            "Last Name": data["last_name"],
            "Email": data["email"],
            "Phone Number": data["phone_number"],
            "User ID": user_id
        }

        # Create booking via Bubble API
        response = requests.post(
            BOOKING_API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json=booking_payload
        )

        bubble_response = response.json()
        if response.status_code == 200 and bubble_response.get("status") == "success":
            return {"message": "Booking created successfully!", "id": bubble_response.get("id")}, 200
        else:
            return {"error": f"Failed to create booking: {bubble_response}"}, response.status_code
    except Exception as e:
        return {"error": f"Error creating booking: {str(e)}"}, 500


if __name__ == "__main__":
    app.run(debug=True)
