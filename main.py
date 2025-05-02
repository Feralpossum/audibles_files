import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import requests
from pathlib import Path

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

# Download WAV file if not already present
AUDIO_DIR = Path("audio")
AUDIO_DIR.mkdir(exist_ok=True)
WAV_FILE = AUDIO_DIR / "piano2.wav"
WAV_URL = "https://www.kozco.com/tech/piano2.wav"

if not WAV_FILE.exists():
    print(f"⬇️ Downloading test WAV file from {WAV_URL}")
    r = requests.get(WAV_URL)
    r.raise_for_status()
    with open(WAV_FILE, "wb") as f:
        f.write(r.content)
    print("✅ Downloaded piano2.wav")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=int(GUILD_ID)))
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

@tree.command(name="testaudio", description="Play test WAV audio", guild=discord.Object(id=int(GUILD_ID)))
async def test_audio(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❗ Join a voice channel first.", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel
    vc = await voice_channel.connect()
    vc.play(discord.FFmpegPCMAudio(source=str(WAV_FILE)))

    await interaction.response.send_message(f"🔊 Playing: `{WAV_FILE.name}`", ephemeral=True)

    while vc.is_playing():
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=1))

    await vc.disconnect()

bot.run(TOKEN)
