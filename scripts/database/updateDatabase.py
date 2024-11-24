import requests
import json
import os
import time
from dotenv import load_dotenv
import os
load_dotenv('settings/apikey.env')
api_key = os.getenv("apikey")

def get_level(exp):
    """Converts experience points to level."""
    level = 100 * int(exp / 487000)
    exp = exp % 487000
    if exp < 500:
        return level + exp / 500
    level += 1
    if exp < 3500:
        return level + (exp - 500) / 1000
    level += 1
    if exp < 7000:
        return level + (exp - 3500) / 3500
    level += 1
    exp -= 7000
    return level + exp / 5000

def update_data(api_key, uuid, username):
    """Fetches Hypixel data for a given UUID and updates the data structure if index > 50."""
    url = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"
    
    try:
        while True:  # Retry loop for handling rate limits
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['success']:
                    rank = data.get('player', {}).get('monthlyPackageRank', {})

                    # Extract Bedwars stats
                    bedwars_stats = data.get('player', {}).get('stats', {}).get('Bedwars', {})

                    # Extract active cosmetics
                    active_cosmetics = {key: value for key, value in bedwars_stats.items() if key.startswith("active")}
                    exp = bedwars_stats.get('Experience', 0)
                    star = get_level(exp)
                    final_kills = bedwars_stats.get('final_kills_bedwars', 0)
                    final_deaths = bedwars_stats.get('final_deaths_bedwars', 1)
                    fkdr = final_kills / final_deaths
                    hawk = fkdr / 2
                    tuah = hawk * hawk
                    index = tuah * star
                    timestamp = f'{int(time.time())}'

                    # Update only if the index is above 50
                    if index > 50:
                        existing_data[uuid] = {
                            "username": username.lower(),
                            "mvp++": rank.lower() if isinstance(rank, str) else rank,
                            "index": index,
                            "star": star,
                            "fkdr": fkdr,
                            "lastupdate": timestamp,
                            "activecosmetics": {k: (v.lower() if isinstance(v, str) else v) for k, v in active_cosmetics.items()}
                        }
                        print(f"[Total: {counter - start}] | Data for {username} updated successfully. ({index:.2f})")
                        time.sleep(2)  # Cooldown only applied when data is updated
                    else:
                        print(f"[Total: {counter - start}] | Skipped {username} | {index:.2f}")
                    break  # Exit the retry loop once successful
                else:
                    print("API key or UUID might be incorrect.")
                    break  # Exit the retry loop for invalid keys/UUIDs

            elif response.status_code == 429:
                print("Rate limit hit. Retrying in 5 seconds...")
                time.sleep(5)  # Wait for 5 seconds before retrying

            else:
                print(f"Failed to fetch data for {username}. HTTP Status Code: {response.status_code}")
                break  # Exit the loop for other HTTP errors

    except Exception as e:
        print(f"An error occurred while fetching data for {username}: {e}")



# Load existing data from 'cosmetics.json' if it exists
if os.path.exists('json/cosmetics.json'):
    with open('json/cosmetics.json', 'r', encoding='utf-8') as uuid_file:
        existing_data = json.load(uuid_file)
else:
    existing_data = {}

# Loop through each UUID in cosmetics.json and update Hypixel data
start = 0
counter = start  # Counter to track the number of UUIDs processed

# Convert existing_data to a list of items to allow for indexed access
uuid_list = list(existing_data.items())

for idx, (uuid, player_data) in enumerate(uuid_list):
    # Skip entries up to the current counter position
    if idx < counter:
        continue
    
    username = player_data.get("username")
    if username:
        update_data(api_key, uuid, username)
        counter += 1
        # Save progress periodically
        if counter % 10 == 1:
            with open('json/cosmetics.json', 'w', encoding='utf-8') as uuid_file:
                json.dump(existing_data, uuid_file, indent=4, ensure_ascii=False)
            print(f"Update saved. Total session uuids: {counter - start - 1}")

# Final save to ensure all data is written
with open('json/cosmetics.json', 'w', encoding='utf-8') as uuid_file:
    json.dump(existing_data, uuid_file, indent=4, ensure_ascii=False)

print("All data has been successfully updated in 'cosmetics.json'.")
