import json

with open('json/hypixel_data_mustangk.json', "r") as f:
    data = json.load(f)


pets = data.get('petStats')



print(pets)