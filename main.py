
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

# Bypass Opus check to allow FFmpeg-only playback
discord.opus._lib = True

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
guild_env = os.getenv("GUILD_ID")
if not TOKEN or not guild_env:
    raise RuntimeError("❌ DISCORD_BOT_TOKEN or GUILD_ID is missing from environment variables.")
GUILD_ID = int(guild_env)

MP3_BASE_URL = "https://audibles-files-karls-projects-20dd944d.vercel.app/"

mp3_files = [
    "Sandwich.mp3",
    "ReallyLonelyBeingYou.mp3",
    "Pleasestandstill.mp3",
    "NotEvenSameZipCodeFunny.mp3",
    "Mwahahaha.mp3",
    "MmmRoar.mp3",
    "LovesmeLovesmeNot.mp3",
    "KeepPunching.mp3",
    "INeverWinYouSuck.mp3",
    "GreatestEVER.mp3",
    "FromADrunkenMonkey.mp3",
    "FatGuysNoMoney.mp3",
    "DontSlipMoppingFloor.mp3",
    "DoneLosing.mp3",
    "Boo.mp3"
]

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

class SoundSelect(discord.ui.Select):
    def __init__(self, vc):
        options = [
            discord.SelectOption(label=name.replace(".mp3", ""), value=name)
            for name in mp3_files
        ]
        super().__init__(placeholder="Choose a sound to play...", min_values=1, max_values=1, options=options)
        self.vc = vc

    async def callback(self, interaction: discord.Interaction):
        mp3_url = f"{MP3_BASE_URL}{self.values[0]}"
        self.vc.stop()
        self.vc.play(
            discord.FFmpegPCMAudio(mp3_url),
            after=lambda e: asyncio.run_coroutine_threadsafe(self.vc.disconnect(), bot.loop)
        )
        await interaction.response.send_message(f"▶️ Playing: `{self.values[0]}`", ephemeral=True)

class SoundView(discord.ui.View):
    def __init__(self, vc):
        super().__init__()
        self.add_item(SoundSelect(vc))

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.tree.command(
    name="audibles",
    description="Play an MP3 from the dropdown",
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
