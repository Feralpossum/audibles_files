import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import requests
from pathlib import Path
import sys

# Voice patching
original_play = discord.VoiceClient.play
def patched_play(self, source, *, after=None):
    self.source = source
    self._connected = True
    self._playing = True
    self._end_event.clear()
    self._player = self.loop.create_task(self._play_audio(source, after))
discord.VoiceClient.play = patched_play

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID_RAW = os.getenv("GUILD_ID")

print("🔍 Checking environment variables...")
print(f"DISCORD_BOT_TOKEN is {'set' if TOKEN else 'NOT SET'}")
print(f"GUILD_ID is: {GUILD_ID_RAW}")

if not TOKEN or not GUILD_ID_RAW:
    print("❌ ERROR: Missing DISCORD_BOT_TOKEN or GUILD_ID. Exiting.")
    sys.exit(1)

GUILD_ID = int(GUILD_ID_RAW)

# Test audio file
TEST_FILES = {
    "Piano.wav": "https://www.kozco.com/tech/piano2.wav"
}

Path("audio").mkdir(exist_ok=True)
for name, url in TEST_FILES.items():
    dest = Path("audio") / name
    if not dest.exists():
        try:
            print(f"⬇️ Downloading {name} from {url}")
            r = requests.get(url)
            r.raise_for_status()
            with open(dest, "wb") as f:
                f.write(r.content)
            print(f"✅ Downloaded {name}")
        except Exception as e:
            print(f"❌ Failed to download {name}: {e}", file=sys.stderr)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

class SoundSelect(discord.ui.Select):
    def __init__(self, vc):
        options = [discord.SelectOption(label=f.replace(".wav", ""), value=f) for f in TEST_FILES]
        super().__init__(placeholder="Choose a WAV...", options=options)
        self.vc = vc

    async def callback(self, interaction: discord.Interaction):
        try:
            file_path = f"audio/{self.values[0]}"
            self.vc.stop()
            self.vc.play(
                discord.FFmpegPCMAudio(file_path),
                after=lambda e: asyncio.run_coroutine_threadsafe(self.vc.disconnect(), bot.loop)
            )
            print(f"▶️ Playing: {file_path}")
            await interaction.response.send_message(f"▶️ Playing: {self.values[0]}", ephemeral=True)
        except Exception as e:
            print(f"Playback error: {e}", file=sys.stderr)
            await interaction.response.send_message("❌ Error playing sound.", ephemeral=True)

class SoundView(discord.ui.View):
    def __init__(self, vc):
        super().__init__()
        self.add_item(SoundSelect(vc))

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.tree.command(
    name="audibles",
    description="Play a test WAV file",
    guild=discord.Object(id=GUILD_ID)
)
async def audibles(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❗ Join a voice channel first.", ephemeral=True)
        return
    try:
        vc = await interaction.user.voice.channel.connect()
    except discord.ClientException:
        vc = interaction.guild.voice_client

    await interaction.response.send_message("🎶 Choose a sound to play:", view=SoundView(vc), ephemeral=True)

@bot.event
async def setup_hook():
    print("🔁 Running setup_hook()...")
    try:
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print("✅ Slash command '/audibles' registered to guild")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}", file=sys.stderr)

bot.run(TOKEN)
