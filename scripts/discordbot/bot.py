import discord
from discord import app_commands
from discord.ext import commands
import subprocess
import json
from dotenv import load_dotenv
import os
import logging

# Configure logging to output to the console
logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(message)s", 
    handlers=[
        logging.StreamHandler()  
    ]
)

# Set up intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Initialize bot with intents
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    # Sync the application commands (slash commands) to Discord
    await bot.tree.sync()


# Load the JSON file with valid options
with open("json/possiblecosmetics.json", "r", encoding="utf-8") as f:
    valid_answers = json.load(f)

# Function to check if the user input is valid
# Function to check if the user input is valid
def is_valid_input(attribute_name, user_input):
    if user_input is None:
        return False
    # Check if the user input is in the list of valid options for the attribute
    return user_input.lower() in [value.lower() for value in valid_answers.get(attribute_name, [])]

# Autocomplete function
def make_autocomplete(attribute_name):
    async def autocomplete_options(interaction: discord.Interaction, current: str):
        # Fetch the list of possible options for the attribute
        options = valid_answers.get(attribute_name, [])
        # Filter the options based on the user's input (case-insensitive)
        filtered = [option for option in options if current.lower() in option.lower()]
        # Limit to 25 results (Discord API limit for autocomplete)
        return [app_commands.Choice(name=option, value=option) for option in filtered[:25]]
    return autocomplete_options

# Register the command with autocomplete
@bot.tree.command(name="denick", description="Set active cosmetics for various items")
@app_commands.describe(
    activeislandtopper="Choose an island topper",
    activeglyph="Choose a glyph",
    activeprojectiletrail="Choose a projectile trail",
    activevictorydance="Choose a victory dance",
    activesprays="Choose a spray",
    activedeathcry="Choose a death cry",
    activenpcskin="Choose an NPC skin",
    activekilleffect="Choose a kill effect",
    activekillmessages="Choose a kill message",
    activebeddestroy="Choose a bed destroy effect",
    activewoodtype="Choose a wood type"
)
@app_commands.autocomplete(
    activeislandtopper=make_autocomplete("activeislandtopper"),
    activeglyph=make_autocomplete("activeglyph"),
    activeprojectiletrail=make_autocomplete("activeprojectiletrail"),
    activevictorydance=make_autocomplete("activevictorydance"),
    activesprays=make_autocomplete("activesprays"),
    activedeathcry=make_autocomplete("activedeathcry"),
    activenpcskin=make_autocomplete("activenpcskin"),
    activekilleffect=make_autocomplete("activekilleffect"),
    activekillmessages=make_autocomplete("activekillmessages"),
    activebeddestroy=make_autocomplete("activebeddestroy"),
    activewoodtype=make_autocomplete("activewoodtype")
)
async def denick(
    interaction: discord.Interaction,
    activeislandtopper: str = None,
    activeglyph: str = None,
    activeprojectiletrail: str = None,
    activevictorydance: str = None,
    activesprays: str = None,
    activedeathcry: str = None,
    activenpcskin: str = None,
    activekilleffect: str = None,
    activekillmessages: str = None,
    activebeddestroy: str = None,
    activewoodtype: str = None
):
    # Default to "None" if no value is passed or if the input is invalid
    attributes = {
        "Active Island Topper": activeislandtopper if is_valid_input("activeislandtopper", activeislandtopper) else None,
        "Active Glyph": activeglyph if is_valid_input("activeglyph", activeglyph) else None,
        "Active Projectile Trail": activeprojectiletrail if is_valid_input("activeprojectiletrail", activeprojectiletrail) else None,
        "Active Victory Dance": activevictorydance if is_valid_input("activevictorydance", activevictorydance) else None,
        "Active Sprays": activesprays if is_valid_input("activesprays", activesprays) else None,
        "Active Death Cry": activedeathcry if is_valid_input("activedeathcry", activedeathcry) else None,
        "Active NPC Skin": activenpcskin if is_valid_input("activenpcskin", activenpcskin) else None,
        "Active Kill Effect": activekilleffect if is_valid_input("activekilleffect", activekilleffect) else None,
        "Active Kill Messages": activekillmessages if is_valid_input("activekillmessages", activekillmessages) else None,
        "Active Bed Destroy": activebeddestroy if is_valid_input("activebeddestroy", activebeddestroy) else None,
        "Active Wood Type": activewoodtype if is_valid_input("activewoodtype", activewoodtype) else None,
    }

    # Filter out any attributes with value "None"
    filtered_attributes = {key: value for key, value in attributes.items() if value is not None}

    # Log the user's command input and settings
    user_info = f"User: {interaction.user.name}#{interaction.user.discriminator} (ID: {interaction.user.id})"
    command_info = f"Command: denick | Settings: {filtered_attributes if filtered_attributes else 'No valid settings'}"
    logging.info(f"{user_info} - {command_info}")

    # Create the response message only with non-None attributes
    response = "Here are your active settings:\n"
    for key, value in filtered_attributes.items():
        response += f"**{key}:** {value}\n"

    # If no valid settings were chosen, inform the user
    if not filtered_attributes:
        response = "No valid settings were provided."

    # Create a new dictionary to overwrite the file
    new_data = {
        "cosmetics": filtered_attributes
    }

    # Write the new data to 'denickfilter.json' (overwrites the file)
    with open("json/denickfilter.json", "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)

    try:
        result = subprocess.run(["python", 'scripts/discordbot/botscripts/denick.py'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        # Capture the output from stdout and stderr
        output = result.stdout.strip()
        error_output = result.stderr.strip()    
        if output:
            response += f"\n**Denick**:\n{output}"
        if error_output:
            response += f"\nScript Error Output:\n{error_output}"

    except subprocess.CalledProcessError as e:
        response += f"\nThere was an error running the script: {e}"

    # Replace underscores in the final response before sending it
    response = response.replace("_", "\\_")
    await interaction.response.send_message(response)

load_dotenv('settings/token.env')  # Load the .env file
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
# Run the bot
bot.run(TOKEN)
