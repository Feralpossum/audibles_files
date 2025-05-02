import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

# Bot setup
intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)
tree = client.tree  # Correct way to use command tree in discord.py v2+

# Download test file at container startup
import requests
url = "https://www.kozco.com/tech/piano2.wav"
filename = "piano2.wav"
if not os.path.exists(filename):
    print(f"⬇️ Downloading test WAV file from {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Downloaded {filename}")
    except Exception as e:
        print(f"Failed to download test file: {e}")

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    try:
        synced = await tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Slash command '/testaudio' registered ({len(synced)} commands)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@tree.command(name="testaudio", description="Play a test WAV file in your voice channel")
async def test_audio(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ You must be in a voice channel to use this command.", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel
    try:
        vc = await voice_channel.connect()
    except discord.ClientException:
        vc = discord.utils.get(client.voice_clients, guild=interaction.guild)

    await interaction.response.send_message("🔊 Playing test WAV file...", ephemeral=True)

    vc.play(discord.FFmpegPCMAudio(source=filename), after=lambda e: print(f"Playback done: {e}" if e else "Finished successfully."))

    while vc.is_playing():
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=1))

    await vc.disconnect()

client.run(TOKEN)
