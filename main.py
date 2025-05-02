
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import requests
from pathlib import Path
import sys

# Monkey patch VoiceClient to bypass opus encoder setup
original_play = discord.VoiceClient.play

def patched_play(self, source, *, after=None):
    self.source = source
    self._connected = True
    self._playing = True
    self._end_event.clear()
    self._player = self.loop.create_task(self._play_audio(source, after))
discord.VoiceClient.play = patched_play

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
guild_env = os.getenv("GUILD_ID")
if not TOKEN or not guild_env:
    raise RuntimeError("❌ DISCORD_BOT_TOKEN or GUILD_ID is missing from environment variables.")
GUILD_ID = int(guild_env)

MP3_BASE_URL = "https://audiblesfiles.vercel.app/Audibles/"
mp3_files = [
    "Sandwich.mp3", "ReallyLonelyBeingYou.mp3", "Pleasestandstill.mp3",
    "NotEvenSameZipCodeFunny.mp3", "Mwahahaha.mp3", "MmmRoar.mp3",
    "LovesmeLovesmeNot.mp3", "KeepPunching.mp3", "INeverWinYouSuck.mp3",
    "GreatestEVER.mp3", "FromADrunkenMonkey.mp3", "FatGuysNoMoney.mp3",
    "DontSlipMoppingFloor.mp3", "DoneLosing.mp3", "Boo.mp3"
]

# Create audio directory and download all MP3s locally
Path("audio").mkdir(exist_ok=True)
for file in mp3_files:
    dest = Path("audio") / file
    if not dest.exists():
        try:
            print(f"⬇️ Downloading {file}...")
            r = requests.get(MP3_BASE_URL + file)
            r.raise_for_status()
            with open(dest, "wb") as f:
                f.write(r.content)
            print(f"✅ Downloaded {file}")
        except Exception as e:
            print(f"❌ Failed to download {file}: {e}", file=sys.stderr)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

class SoundSelect(discord.ui.Select):
    def __init__(self, vc):
        options = [discord.SelectOption(label=f.replace(".mp3", ""), value=f) for f in mp3_files]
        super().__init__(placeholder="Choose a sound to play...", options=options)
        self.vc = vc

    async def callback(self, interaction: discord.Interaction):
        path = f"audio/{self.values[0]}"
        try:
            self.vc.stop()
            self.vc.play(
                discord.FFmpegPCMAudio(path),
                after=lambda e: asyncio.run_coroutine_threadsafe(self.vc.disconnect(), bot.loop)
            )
            await interaction.response.send_message(f"▶️ Playing: `{self.values[0]}`", ephemeral=True)
        except Exception as e:
            print(f"Playback error: {e}", file=sys.stderr)
            await interaction.response.send_message("❌ Failed to play audio. Check logs.", ephemeral=True)

class SoundView(discord.ui.View):
    def __init__(self, vc):
        super().__init__()
        self.add_item(SoundSelect(vc))

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.tree.command(
    name="audibles",
    description="Play a local MP3 from the dropdown",
    guild=discord.Object(id=GUILD_ID)
)
async def audibles(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❗ Join a voice channel first.", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel
    vc = await voice_channel.connect()
    view = SoundView(vc)
    await interaction.response.send_message("🎵 Choose a sound to play:", view=view, ephemeral=True)

@bot.event
async def setup_hook():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print("✅ Slash command '/audibles' registered directly to guild")

bot.run(TOKEN)
