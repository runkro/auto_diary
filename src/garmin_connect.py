from garminconnect import Garmin, GarminConnectAuthenticationError
import json

try:
    # Attempt to load a previous session
    with open("session.json") as f:
        saved_session = json.load(f)
        client = Garmin(session_data=saved_session)
        client.login()
except (FileNotFoundError, GarminConnectAuthenticationError):
    # Login with credentials if session is invalid or not present
    client = Garmin()
    client.login("runar.kroyer@gmail.com", "Oakley95")
    # Save session for future use
    with open("session.json", "w") as f:
        json.dump(client.session_data, f)


# Fetch activities
activities = client.get_activities(0, 10)  # Fetch last 10 activities

# Edit the title of a specific workout
activity_id = activities[0]['activityId']  # Example: first activity ID
new_title = "Updated Workout Title"
client.update_activity(activity_id, {"title": new_title})