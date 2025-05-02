import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
import requests
from pathlib import Path

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

INTENTS = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=INTENTS)
WAV_URL = "https://www.kozco.com/tech/piano2.wav"
WAV_PATH = "piano2.wav"

# Download the test WAV file at container start
if not Path(WAV_PATH).exists():
    print(f"⬇️ Downloading test WAV file from {WAV_URL}")
    response = requests.get(WAV_URL)
    with open(WAV_PATH, "wb") as f:
        f.write(response.content)
    print("✅ Downloaded piano2.wav")

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    try:
        synced = await client.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Slash command '/testaudio' registered ({len(synced)} commands)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@client.tree.command(name="testaudio", description="Play test WAV audio", guild=discord.Object(id=GUILD_ID))
async def test_audio(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ You must be in a voice channel to use this command.", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel
    try:
        vc = await voice_channel.connect()
    except discord.ClientException:
        vc = discord.utils.get(client.voice_clients, guild=interaction.guild)

    if not vc:
        await interaction.response.send_message("❌ Could not join the voice channel.", ephemeral=True)
        return

    source = discord.FFmpegPCMAudio(WAV_PATH)
    vc.play(source)

    await interaction.response.send_message(f"🔊 Playing `{WAV_PATH}`...", ephemeral=True)

    while vc.is_playing():
        await asyncio.sleep(1)

    await vc.disconnect()

client.run(TOKEN)

