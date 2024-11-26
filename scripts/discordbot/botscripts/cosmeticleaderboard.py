import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

def denick(cosmetics_file, search_criteria, indexfilter):
    try:
        # Load the JSON data
        with open(cosmetics_file, 'r') as file:
            data = json.load(file)
        
        # Remove null criteria from the search_criteria
        search_criteria = {key: value for key, value in search_criteria.items() if value is not None}
        
        # Filter users based on search criteria
        matching_users = []
        for user_id, user_data in data.items():
            active_cosmetics = user_data.get("activecosmetics", {})
            mvp_status = user_data.get("mvp++", "")  # Get mvp++ field
            
            # Ensure mvp_status is a string (if it's not already)
            if isinstance(mvp_status, str):
                mvp_status = mvp_status.lower()
            else:
                mvp_status = ""  # Default to empty string if mvp_status is not a string
                
            index = user_data.get("index", "")
            
            # Check if all search criteria match (case insensitive comparison)
            criteria_match = all(
                active_cosmetics.get(key, "").lower() == str(value).lower()  # Ensure both sides are lowercase
                for key, value in search_criteria.items()
            )
            
            if criteria_match and mvp_status == "superstar" and int(index) > indexfilter:
                matching_users.append({
                    "username": user_data.get("username", "Unknown"),
                    "index": user_data.get("index", 0),
                    "star": user_data.get("star", 0),
                    "fkdr": user_data.get("fkdr", 0),
                    "lastupdate": user_data.get("lastupdate", 0),
                    "uuid": user_id
                })
        
        # Sort by 'index' in descending order
        matching_users.sort(key=lambda x: x["index"], reverse=True)

        # Limit to a maximum of 10 users
        return matching_users[:10]
    
    except FileNotFoundError:
        print(f"Error: File '{cosmetics_file}' not found.")
        return []
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON data.")
        return []
    
# Example usage
if __name__ == "__main__":
    # Path to your JSON file
    cosmetics_file = 'json/cosmetics.json'
    
    with open('json/cosmeticleaderboardfilter.json', 'r') as file:
        filter = json.load(file)
    
    # Index filter value
    indexfilter = 500
    
    key_mapping = {
        "Active Island Topper": "activeIslandTopper",
        "Active Glyph": "activeGlyph",
        "Active Projectile Trail": "activeProjectileTrail",
        "Active Victory Dance": "activeVictoryDance",
        "Active Sprays": "activeSprays",
        "Active Death Cry": "activeDeathCry",
        "Active NPC Skin": "activeNPCSkin",
        "Active Kill Effect": "activeKillEffect",
        "Active Kill Messages": "activeKillMessages",
        "Active Bed Destroy": "activeBedDestroy",
        "Active Wood Type": "activeWoodType"
    }

    if "cosmetics" in filter:
        renamed_cosmetics = {key_mapping.get(k, k): v for k, v in filter["cosmetics"].items()}  # Use get to handle unmapped keys
    else:
        renamed_cosmetics = {}
    chillguy = {"cosmetics": renamed_cosmetics}
    search_criteria = chillguy.get('cosmetics')

    # Get matching users
    results = denick(cosmetics_file, search_criteria, indexfilter)
    
    # Print results
    if results:
        print(f"Users matching the criteria ({len(results)} found):")
        placement = 1
        for user in results:
            print(f"#{placement} **[{round(user['star'])}]☆** {user['username']} | **FKDR**: {round(user['fkdr'], 2)}, | || UUID: {user['uuid']} | Updated:<t:{user.get('lastupdate')}:R>||")
            placement += 1 
    else:
        print("No users found matching the criteria.")
