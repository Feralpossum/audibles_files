import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import requests

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", 0))
WAV_URL = "https://www.kozco.com/tech/piano2.wav"
WAV_PATH = "piano2.wav"

# Download test .wav if not present
if not Path(WAV_PATH).exists():
    print(f"⬇️ Downloading test WAV file from {WAV_URL}")
    r = requests.get(WAV_URL)
    with open(WAV_PATH, "wb") as f:
        f.write(r.content)
    print("✅ Downloaded piano2.wav")

intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    try:
        synced = await client.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Slash command '/testaudio' registered ({len(synced)} commands)")
    except Exception as e:
        print(f"❌ Error registering commands: {e}")

@client.tree.command(name="testaudio", description="Play the test audio", guild=discord.Object(id=GUILD_ID))
async def test_audio(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ You must be in a voice channel!", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel
    try:
        vc = await voice_channel.connect()
    except discord.ClientException:
        vc = interaction.guild.voice_client

    vc.play(discord.FFmpegPCMAudio(WAV_PATH))
    await interaction.response.send_message("🔊 Playing test audio...", ephemeral=True)

    while vc.is_playing():
        await asyncio.sleep(1)
    await vc.disconnect()

client.run(TOKEN)
