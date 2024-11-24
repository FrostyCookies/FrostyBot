import requests
import json
import os
import time
import logging
from dotenv import load_dotenv

# Initialize dotenv
load_dotenv('settings/apikey.env')
api_key = os.getenv("apikey")

# Setup logging to both console and file
log_file_path = 'scripts/database/log.txt'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler(log_file_path, mode='a', encoding='utf-8')  # Log to file
    ]
)
logger = logging.getLogger()

# Load the list of usernames from 'sample.json'
with open('json/players.json', 'r', encoding='utf-8') as file:
    players = json.load(file)

def getuuid(username):
    """Fetches UUID from Mojang API for a given username."""
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['id']
    else:
        logger.error(f"Failed to retrieve UUID for {username}")
        return None

# Load existing data from 'cosmetics.json' if it exists
if os.path.exists('json/cosmetics.json'):
    with open('json/cosmetics.json', 'r', encoding='utf-8') as uuid_file:
        existing_data = json.load(uuid_file)
else:
    existing_data = {}

# Convert experience to star level
def get_level(y):
    level = 100 * int(y / 487000)
    y = y % 487000
    if y < 500:
        return level + y / 500
    level += 1
    if y < 3500:
        return level + (y - 500) / 1000
    level += 1
    if y < 3500:
        return level + (y - 1500) / 2000
    if y < 7000:
        return level + (y - 3500) / 3500
    level += 1
    y -= 7000
    return level + y / 5000

# Function to fetch Hypixel data for a player and store it
def getdata(api_key, uuid, username):
    """Fetches Hypixel data for a given UUID and adds it to the existing data structure."""
    url = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"
    
    while True:
        try:
            # Make a request to the Hypixel API
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                
                if data['success']:
                    # Extract rank without changing case
                    rank = data.get('player', {}).get('monthlyPackageRank') if data.get('player', {}).get('monthlyPackageRank') else "none"
                    
                    # Extract Bedwars stats
                    bedwars_stats = data.get('player', {}).get('stats', {}).get('Bedwars', {})
                    
                    # Extract active cosmetics without changing key case
                    active_cosmetics = {key: str(value) for key, value in bedwars_stats.items() if key.startswith("active")}
                    
                    exp = bedwars_stats.get('Experience', 0)
                    star = get_level(exp)
                    finalkills = bedwars_stats.get('final_kills_bedwars', 0)
                    finaldeaths = bedwars_stats.get('final_deaths_bedwars', 1)
                    fkdr = finalkills / finaldeaths
                    hawk = fkdr / 2
                    tuah = hawk * hawk
                    index = tuah * star

                    timestamp = f'{int(time.time())}'

                    # Ensure existing_data is updated without altering key case
                    if uuid not in existing_data:
                        existing_data[uuid] = {"username": username, "hypixel_data": {}}
                    existing_data[uuid]["mvp++"] = rank.lower()
                    existing_data[uuid]["index"] = index
                    existing_data[uuid]["star"] = star
                    existing_data[uuid]["fkdr"] = fkdr
                    existing_data[uuid]["lastupdate"] = timestamp
                    existing_data[uuid]["activecosmetics"] = active_cosmetics

                    logger.info(f"Data for {username} added successfully.")
                else:
                    logger.warning("API key or UUID might be incorrect.")
                break  # Exit the loop after a successful response

            elif response.status_code == 429:
                logger.warning("Rate limit exceeded. Waiting for 20 seconds before retrying...")
                time.sleep(20)

            else:
                logger.error(f"Failed to fetch data for {username}. HTTP Status Code: {response.status_code}")
                break  # Exit the loop for non-retryable errors

        except Exception as e:
            logger.error(f"An error occurred while fetching data for {username}: {e}")
            break  # Exit the loop if an exception occurs

starting_point = 3250  
count = starting_point
save_interval = 10

for index, username in enumerate(players[starting_point:], start=starting_point):
    username = username.lower()  # Ensure username is lowercase
    uuid = getuuid(username)
    if uuid:
        if uuid not in existing_data:
            existing_data[uuid] = {"username": username}

        getdata(api_key, uuid, username)
        count += 1
        
        # Save progress during intervals
        if count % save_interval == 0:
            with open('json/cosmetics.json', 'w', encoding='utf-8') as uuid_file:
                json.dump(existing_data, uuid_file, indent=4, ensure_ascii=False)
            logger.info(f"Progress saved. Session players: {count}")

        time.sleep(1.2)

# Final save at the end
with open('json/cosmetics.json', 'w', encoding='utf-8') as uuid_file:
    json.dump(existing_data, uuid_file, indent=4, ensure_ascii=False)

logger.info("All data has been successfully saved to 'cosmetics.json'.")
