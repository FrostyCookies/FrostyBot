import json
from datetime import datetime

def GetTop(file_path, amount, category):
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Convert 'lastupdate' to readable time and filter relevant users
    formatted_data = {
        user_id: {
            **user_info,
            "readable_lastupdate": datetime.fromtimestamp(int(user_info["lastupdate"])).strftime('%Y-%m-%d %H:%M:%S')
        }
        for user_id, user_info in data.items()
        if category in user_info
    }

    # Sort users by the specified category
    sorted_users = sorted(
        formatted_data.items(),
        key=lambda item: item[1][category],
        reverse=True
    )

    # Get top users and include last update in output
    top_users = [
        f"{user_info['username']} has got the {category}: {round(user_info[category], 2)} (Last update: {user_info['readable_lastupdate']})"
        for _, user_info in sorted_users[:amount]
    ]

    return top_users

# Specifications
file_path = 'json/cosmetics.json'
amount = 25
category = 'index'

top = GetTop(file_path, amount, category)
print("\n".join(top))
