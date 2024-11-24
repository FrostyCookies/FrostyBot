
import requests
import json

def get_minecraft_uuid(username):

    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    

    response = requests.get(url)


    if response.status_code == 200:

        data = response.json()
        return data['id']



def get_hypixel_data(api_key, uuid):
    url = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"
    
    try:

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data['success']:
                return data['player'] 
        else:
            print("api key or uuid wrong")

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def write_data_to_file(data, username):
    filename=f"json/hypixel_data_{username}.json"

    bedwars_stats = data.get('stats', {}).get('Bedwars', {})    
    active_cosmetics = {key: value for key, value in bedwars_stats.items() if key.startswith("active")}
    try:
        with open(filename, 'w') as f:

           json.dump(data, f, indent=4) 
        print(f"Data written to {filename}")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")







if __name__ == "__main__":
    username = "mustangk"
    uuid = get_minecraft_uuid(username)

    hypixel_api_key = "8cbe4410-e527-47b5-8da2-fc2033d16ada"
    

    player_data = get_hypixel_data(hypixel_api_key, uuid)
    if player_data:
        write_data_to_file(player_data, username)
