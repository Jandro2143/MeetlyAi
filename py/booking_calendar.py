from flask import render_template, request
from pyairtable import Table
from dateutil import parser
import pytz
from config import Config  # Importing the Config class
import logging


def get_airtable_table(table_name):
    """Retrieve the Airtable table using the Config class."""
    airtable_api_key = Config.AIRTABLE_API_KEY
    base_id = Config.BASE_ID
    return Table(airtable_api_key, base_id, table_name)

def calendar(user_id):
    """Fetch bookings for a specific user and render the calendar template."""
    try:
        table = get_airtable_table(Config.BOOKINGS_TABLE)  # Use Config.BOOKINGS_TABLE
        
        # Query Airtable for records matching the user_id
        records = table.all(formula=f"{{User ID}} = '{user_id}'")
        booked_slots = {}

        for record in records:
            fields = record["fields"]
            if "Date/time" in fields:  # Match the Airtable field name
                booking_date = parser.parse(fields["Date/time"]).astimezone(pytz.timezone("Australia/Sydney"))
                day = booking_date.strftime("%Y-%m-%d")
                time = booking_date.strftime("%I:%M %p")
                if day not in booked_slots:
                    booked_slots[day] = []
                booked_slots[day].append(time)

        # Pass booked_slots and user_id to the template
        return render_template("calendar.html", booked_slots=booked_slots, user_id=user_id)
    except Exception as e:
        return render_template("error.html", error_message=f"Error fetching data: {str(e)}"), 500

def book(user_id):
    """Create a new booking in Airtable."""
    data = request.json

    # Log the incoming payload
    logging.debug(f"Incoming request data: {data}")

    # Check if all required fields (except user_id) are provided
    required_fields = ("first_name", "last_name", "email", "phone_number", "date", "time")
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        logging.debug(f"Missing fields: {missing_fields}")
        return {"message": f"Missing required fields: {', '.join(missing_fields)}"}, 400

    try:
        table = get_airtable_table(Config.BOOKINGS_TABLE)  # Use Config.BOOKINGS_TABLE

        # Parse the provided date and time
        local_datetime_str = f"{data['date']} {data['time']}"
        local_datetime = parser.parse(local_datetime_str)
        utc_datetime = pytz.timezone("Australia/Sydney").localize(local_datetime).astimezone(pytz.utc)

        # Add the record to Airtable, including the User ID from the URL
        new_record = {
            "Name": f"{data['first_name']} {data['last_name']}",
            "Date/time": utc_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "Number": data["phone_number"],
            "Email": data["email"],
            "User ID": user_id,  # User ID from URL
        }

        # Log the record being sent to Airtable
        logging.debug(f"Creating new record: {new_record}")

        table.create(new_record)

        return {"message": "Booking created successfully!"}, 200
    except Exception as e:
        logging.error(f"Error creating booking: {str(e)}")
        return {"message": f"Error creating booking: {str(e)}"}, 500
