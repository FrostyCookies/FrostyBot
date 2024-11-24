import os
import requests
import time
from datetime import datetime
import json




def get_minecraft_username(uuid):
    """Fetches the Minecraft username for a given UUID from the Mojang API."""
    url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'name' in data:
            return data['name']  # Return current username
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching username for UUID {uuid}: {e}")
        return None

def fetch_and_convert_bedwars_leaderboard(api_key):
    """Fetches Bedwars leaderboard from Hypixel API, converts UUIDs to usernames, and outputs the result in JSON format."""
    url = "https://api.hypixel.net/leaderboards"

    try:
        response = requests.get(url, params={"key": api_key})
        response.raise_for_status()
        data = response.json()

        if data.get('success'):
            bedwars_leaderboard = data['leaderboards'].get('BEDWARS', [])

            if not bedwars_leaderboard:
                print("No Bedwars leaderboard data available.")
                return

            wins_count = 0  # Counter for the Wins category
            converted_usernames = {}  # Dictionary to store UUIDs and usernames

            for category in bedwars_leaderboard:
                if category['title'] == "Wins":
                    wins_count += 1
                    if wins_count == 2:  # When it's the second Wins category
                        for uuid in category['leaders']:
                            # Fetch the username for each UUID
                            username = get_minecraft_username(uuid)
                            print(username)
                            if username:
                                data = get_hypixel_data(api_key, uuid)
                                if data:
                                    cosmetic_data = log_data(data)
                                    timestamp = f'{int(time.time())}'
                                    converted_usernames[uuid] = {"username": username, "time": timestamp, "activecosmetics": cosmetic_data}
                            else:
                                converted_usernames[uuid] = {"username": "Username not found"}

                            # Add a longer sleep to avoid rate limiting (1 second)
                            time.sleep(0.1)
                        break

            # Output the final usernames in JSON format
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"json/weekly_{timestamp}.json"

            # Ensure the output directory exists
            os.makedirs(os.path.dirname(output_filename), exist_ok=True)

            # Write the dictionary as JSON to the file
            with open(output_filename, 'w') as file:
                json.dump(converted_usernames, file, indent=2)  # Pretty-print the JSON output

            print(f"Leaderboard usernames written to {output_filename}.")
        else:
            print(f"Error: {data.get('cause', 'Unknown error')}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch leaderboards: {e}")

def get_hypixel_data(api_key, uuid):
    """Fetch player data from the Hypixel API using the UUID."""
    url = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        if data.get('success'):
            return data['player']
        else:
            print("Failed to retrieve player data.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching Hypixel data: {e}")
        return None

def log_data(data):
    """Extracts active Bedwars cosmetics from player data."""
    bedwars_stats = data.get('stats', {}).get('Bedwars', {})
    active_cosmetics = {key: value for key, value in bedwars_stats.items() if key.startswith("active")}

    return active_cosmetics  # Return the dictionary of active cosmetics


hypixel_api_key = "9c3312bf-593d-4e2f-822f-b57dbd97cede"
fetch_and_convert_bedwars_leaderboard(hypixel_api_key)
