
import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
import requests
from datetime import timedelta
from discord.utils import sleep_until, utcnow

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

TEST_AUDIO_URL = "https://www.kozco.com/tech/piano2.wav"
AUDIO_PATH = "piano2.wav"

# Download the test audio file
print(f"⬇️ Downloading test WAV file from {TEST_AUDIO_URL}")
try:
    response = requests.get(TEST_AUDIO_URL)
    response.raise_for_status()
    with open(AUDIO_PATH, "wb") as f:
        f.write(response.content)
    print(f"✅ Downloaded {AUDIO_PATH}")
except Exception as e:
    print(f"❌ Failed to download test audio file: {e}")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = commands.Bot(command_prefix="!", intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name="testaudio", description="Play the test WAV file")
async def test_audio(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❗ Join a voice channel first.", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel

    # Check if already connected
    if interaction.guild.voice_client:
        vc = interaction.guild.voice_client
    else:
        vc = await voice_channel.connect()

    # Play the WAV file
    source = discord.FFmpegPCMAudio(AUDIO_PATH)
    vc.play(source)

    await interaction.response.send_message(f"🔊 Playing `{AUDIO_PATH}`", ephemeral=True)

    # Wait for audio to play
    await sleep_until(utcnow() + timedelta(seconds=1))
    while vc.is_playing():
        await asyncio.sleep(1)

    await vc.disconnect()

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print("✅ Slash command '/testaudio' registered")

client.run(TOKEN)
