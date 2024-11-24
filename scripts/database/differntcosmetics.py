import json

# Load the data from the input file
with open('json/cosmetics.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

cosmetic_types = {}

# Iterate through the users' data
for user_id, user_data in data.items():
    active_cosmetics = user_data.get('activecosmetics', {})
    for cosmetic_type, cosmetic_value in active_cosmetics.items():
        # Ensure both cosmetic type and value are in lowercase
        cosmetic_type_lower = cosmetic_type.lower()
        cosmetic_value_lower = cosmetic_value.lower()
        
        if cosmetic_type_lower not in cosmetic_types:
            cosmetic_types[cosmetic_type_lower] = set()
        cosmetic_types[cosmetic_type_lower].add(cosmetic_value_lower)

# Convert the sets to lists
cosmetic_types = {key: list(values) for key, values in cosmetic_types.items()}

# Save the result with UTF-8 encoding
output_path = 'json/possiblecosmetics.json'
with open(output_path, 'w', encoding='utf-8') as output_file:
    json.dump(cosmetic_types, output_file, indent=4, ensure_ascii=False)

# Print the results
for cosmetic_type, values in cosmetic_types.items():
    print(f"{cosmetic_type}: {len(values)} unique cosmetics")

print(f"Extracted cosmetics saved to {output_path}")
