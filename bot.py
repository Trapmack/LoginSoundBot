import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
import json
import sys
from dotenv import load_dotenv
import aiohttp
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Secure bot token
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    logging.error("DISCORD_TOKEN not found in environment variables.")
    sys.exit(1)

# Tuna credentials (optional, for authenticated searches)
TUNA_TOKEN = os.getenv("TUNA_TOKEN")

# Dynamically set OPUS_LIBRARY
if sys.platform == "darwin":  # macOS
    os.environ["OPUS_LIBRARY"] = "/opt/homebrew/lib/libopus.dylib"
elif sys.platform == "win32":  # Windows
    os.environ["OPUS_LIBRARY"] = "C:/path/to/libopus.dll"
elif sys.platform == "linux":  # Linux
    pass

# Define intents
intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True

# Initialize bot with command tree for slash commands
bot = commands.Bot(command_prefix="!", intents=intents)  # Legacy support (optional)
tree = app_commands.CommandTree(bot)

# Load config with no default folder assumption
def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("config.json not found. Creating empty config.")
        default_config = {"user_sound_map": {}, "default_sound": None, "exit_sound": None}
        with open("config.json", "w") as f:
            json.dump(default_config, f, indent=4)
        return default_config
    except json.JSONDecodeError:
        logging.error("config.json is invalid.")
        sys.exit(1)

config = load_config()
USER_SOUND_MAP = config["user_sound_map"]
DEFAULT_SOUND = config["default_sound"]
EXIT_SOUND = config["exit_sound"]

# Save config
def save_config():
    with open("config.json", "w") as f:
        json.dump({"user_sound_map": USER_SOUND_MAP, "default_sound": DEFAULT_SOUND, "exit_sound": EXIT_SOUND}, f, indent=4)

# Play custom message
async def play_custom_message(vc, custom_sound_path):
    if custom_sound_path and os.path.exists(custom_sound_path):
        vc.play(discord.FFmpegPCMAudio(custom_sound_path))
        while vc.is_playing():
            await asyncio.sleep(1)
        try:
            await vc.disconnect()
        except Exception as e:
            logging.error(f"Failed to disconnect: {e}")
    else:
        logging.warning(f"Sound file {custom_sound_path} not found or not set. Skipping.")
        await vc.disconnect()

# Play exit sound
async def play_exit_sound(vc):
    if EXIT_SOUND and os.path.exists(EXIT_SOUND):
        vc.play(discord.FFmpegPCMAudio(EXIT_SOUND))
        while vc.is_playing():
            await asyncio.sleep(1)
        try:
            await vc.disconnect()
        except Exception as e:
            logging.error(f"Failed to disconnect: {e}")
    else:
        logging.warning("Exit sound not set or not found. Skipping.")
        await vc.disconnect()

# Connect with backoff
async def connect_with_backoff(channel, retry_attempts=5):
    for attempt in range(retry_attempts):
        try:
            vc = await channel.connect()
            return vc
        except discord.errors.ConnectionClosed as e:
            logging.error(f"Connection closed with error: {e}")
            backoff_time = min(2 ** attempt, 32)
            logging.info(f"Retrying in {backoff_time} seconds...")
            await asyncio.sleep(backoff_time)
        except OSError as e:
            logging.error(f"OS error occurred: {e}")
            break
    logging.error("Failed to connect after multiple attempts.")
    return None

# Voice state update event
@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return
    try:
        if after.channel and before.channel != after.channel:
            if member.guild.voice_client is not None:
                await member.guild.voice_client.disconnect()
                await asyncio.sleep(1)

            custom_sound_path = USER_SOUND_MAP.get(str(member.id), DEFAULT_SOUND)
            if custom_sound_path:
                vc = await connect_with_backoff(after.channel)
                if vc:
                    await play_custom_message(vc, custom_sound_path)

        elif before.channel and not after.channel:
            if member.guild.voice_client is not None:
                await member.guild.voice_client.disconnect()
                await asyncio.sleep(1)

            if EXIT_SOUND:
                vc = await connect_with_backoff(before.channel)
                if vc:
                    await play_exit_sound(vc)

    except Exception as e:
        logging.error(f"An error occurred: {e}")

# Slash command: /tunalogin
@tree.command(name="tunalogin", description="Log into Tuna for authenticated searches")
@app_commands.checks.has_permissions(administrator=True)
async def tuna_login(interaction: discord.Interaction):
    login_url = "https://tuna.voicemod.net/login"  # Adjust if Tuna provides a specific URL
    await interaction.response.send_message(f"Please log into Tuna here: {login_url}\nAfter logging in, provide the authorization code with `/tunacode <code>`.")

# Slash command: /tunacode
@tree.command(name="tunacode", description="Submit Tuna authorization code")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(code="The authorization code from Tuna")
async def tuna_code(interaction: discord.Interaction, code: str):
    global TUNA_TOKEN
    async with aiohttp.ClientSession() as session:
        async with session.post("https://tuna.voicemod.net/oauth/token", data={"code": code}) as resp:
            if resp.status == 200:
                data = await resp.json()
                TUNA_TOKEN = data.get("access_token")
                await interaction.response.send_message("Successfully logged into Tuna! You can now use enhanced search with `/importsound`.")
            else:
                await interaction.response.send_message("Failed to authenticate with Tuna. Check the code and try again.")

# Slash command: /adduser
@tree.command(name="adduser", description="Add a user to the sound map")
@app_commands.checks.has_permissions(administrator=True)
async def add_user(interaction: discord.Interaction):
    guild = interaction.guild
    members = [m for m in guild.members if not m.bot]
    if not members:
        await interaction.response.send_message("No members found in this server.")
        return

    options = [discord.SelectOption(label=m.name, value=str(m.id)) for m in members[:25]]
    select = discord.ui.Select(placeholder="Select a member", options=options)

    async def select_callback(select_interaction):
        member_id = select.values[0]
        await select_interaction.response.send_message(f"Selected {members[int(member_id) % len(members)].name} (ID: {member_id}). Specify a sound file path (e.g., ./sounds/example.mp3):")
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        try:
            msg = await bot.wait_for("message", check=check, timeout=60.0)
            sound_path = msg.content.strip()
            if not os.path.exists(sound_path):
                await interaction.followup.send(f"File {sound_path} not found.")
                return
            USER_SOUND_MAP[member_id] = sound_path
            save_config()
            await interaction.followup.send(f"Added {members[int(member_id) % len(members)].name} with sound {sound_path}.")
        except asyncio.TimeoutError:
            await interaction.followup.send("Timed out waiting for sound file path.")

    select.callback = select_callback
    view = discord.ui.View()
    view.add_item(select)
    await interaction.response.send_message("Select a member to add:", view=view)

# Slash command: /importsound
@tree.command(name="importsound", description="Search Tuna for MP3s, preview, and import one")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(search_query="The search term for Tuna sounds")
async def import_sound(interaction: discord.Interaction, search_query: str):
    await interaction.response.defer()  # Defer response since this might take time
    url = f"https://tuna.voicemod.net/sounds?search={search_query.replace(' ', '+')}"
    headers = {"Authorization": f"Bearer {TUNA_TOKEN}"} if TUNA_TOKEN else {}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                await interaction.followup.send("Failed to connect to Tuna. Try again later.")
                return
            text = await resp.text()
            mp3_links = []
            start = 0
            while True:
                start = text.find("https://cdn.tuna.voicemod.net/sounds/", start)
                if start == -1:
                    break
                end = text.find(".mp3", start) + 4
                mp3_links.append(text[start:end])
                start = end

            if not mp3_links:
                await interaction.followup.send(f"No MP3s found for '{search_query}'.")
                return

            options = [discord.SelectOption(label=f"Sound {i+1}", value=str(i), description=link[:50]) for i, link in enumerate(mp3_links[:25])]
            select = discord.ui.Select(placeholder="Select a sound to preview", options=options)

            async def select_callback(select_interaction):
                sound_idx = int(select.values[0])
                sound_url = mp3_links[sound_idx]
                await select_interaction.response.send_message(f"Previewing sound: {sound_url}")

                async with session.get(sound_url) as mp3_resp:
                    if mp3_resp.status == 200:
                        temp_path = f"./sounds/temp_preview_{sound_idx}.mp3"
                        with open(temp_path, "wb") as f:
                            f.write(await mp3_resp.read())
                        
                        if interaction.user.voice and interaction.user.voice.channel:
                            vc = await connect_with_backoff(interaction.user.voice.channel)
                            if vc:
                                await play_custom_message(vc, temp_path)
                        
                        await interaction.followup.send("Type `yes` to import this sound, or anything else to cancel.")
                        def check(m):
                            return m.author == interaction.user and m.channel == interaction.channel
                        try:
                            confirm = await bot.wait_for("message", check=check, timeout=30.0)
                            if confirm.content.lower() == "yes":
                                sound_name = f"{search_query.replace(' ', '_')}_{sound_idx}.mp3"
                                sound_path = f"./sounds/{sound_name}"
                                os.rename(temp_path, sound_path)
                                await interaction.followup.send(f"Imported '{sound_name}' to {sound_path}. Use /adduser to assign it.")
                            else:
                                os.remove(temp_path)
                                await interaction.followup.send("Import cancelled.")
                        except asyncio.TimeoutError:
                            os.remove(temp_path)
                            await interaction.followup.send("Timed out. Import cancelled.")
                    else:
                        await interaction.followup.send("Failed to download sound for preview.")

            select.callback = select_callback
            view = discord.ui.View()
            view.add_item(select)
            await interaction.followup.send(f"Found {len(mp3_links)} sounds for '{search_query}'. Select one to preview:", view=view)

# On ready event with slash command sync
@bot.event
async def on_ready():
    await tree.sync()  # Sync slash commands globally
    logging.info(f"Logged in as {bot.user.name}")
    permissions = discord.Permissions(connect=True, speak=True, read_messages=True, send_messages=True, manage_messages=True)
    invite_url = discord.utils.oauth_url(bot.user.id, permissions=permissions)
    logging.info(f"Invite me with: {invite_url}")

# Error handling for slash commands
async def command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)

tree.on_error = command_error

# Run the bot
bot.run(TOKEN)