from flask import Flask, render_template, request
import requests
from dateutil import parser
import pytz

app = Flask(__name__)

BUBBLE_API_URL = "https://info-54940.bubbleapps.io/version-test/api/1.1/obj/Booking"
API_KEY = "e58f0332d3bf9c0be92f50b2e1871c05"

# Specify your local timezone
LOCAL_TIMEZONE = pytz.timezone("Australia/Sydney")

@app.route("/")
def calendar():
    # Get the user_id from query parameters
    user_id = request.args.get("user_id")
    if not user_id:
        return "Error: user_id is required to fetch bookings.", 400

    response = requests.get(
        f"{BUBBLE_API_URL}?constraints=[{{\"key\":\"User ID\",\"constraint_type\":\"equals\",\"value\":\"{user_id}\"}}]",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )

    if response.status_code != 200:
        return f"Error: Received status code {response.status_code} from the API."

    try:
        bookings = response.json()["response"]["results"]
        booked_slots = {}

        # Organize bookings by day and times
        for booking in bookings:
            if "Date" in booking:
                # Convert UTC time to local timezone
                booking_date = parser.isoparse(booking["Date"]).astimezone(LOCAL_TIMEZONE)
                day = booking_date.strftime("%Y-%m-%d")
                time = booking_date.strftime("%I:%M %p")
                if day not in booked_slots:
                    booked_slots[day] = []
                booked_slots[day].append(time)
    except Exception as e:
        return f"Error parsing JSON: {str(e)}"

    # Debug: Print booked slots in the console
    print("Booked Slots for User:", user_id, booked_slots)

    return render_template("calendar.html", booked_slots=booked_slots, user_id=user_id)


@app.route("/book", methods=["POST"])
def book():
    data = request.json

    # Check if user_id is provided
    user_id = data.get("user_id")
    if not user_id:
        return {"message": "Error: user_id is required to create a booking."}, 400

    # Combine date and time and convert to UTC
    local_datetime = f"{data['date']} {data['time']}"
    local_datetime_obj = parser.parse(local_datetime)
    utc_datetime = LOCAL_TIMEZONE.localize(local_datetime_obj).astimezone(pytz.utc)

    booking_payload = {
        "Date": utc_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z"),  # Bubble.io-compatible format
        "First Name": data["first_name"],
        "Last Name": data["last_name"],
        "Email": data["email"],
        "Phone Number": data["phone_number"],
        "User ID": user_id  # Include user_id in the booking payload
    }

    response = requests.post(
        BUBBLE_API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json=booking_payload
    )

    try:
        bubble_response = response.json()
        if response.status_code == 200 and bubble_response.get("status") == "success":
            return {"message": "Booking created successfully!", "id": bubble_response.get("id")}, 200
        else:
            return {"message": f"Failed to create booking: {bubble_response}"}, response.status_code
    except Exception as e:
        return {"message": f"Error parsing API response: {str(e)}"}, 500


if __name__ == "__main__":
    app.run(debug=True)

