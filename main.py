
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

# Public base URL for hosted MP3 files
MP3_BASE_URL = "https://audibles-files-karls-projects-20dd944d.vercel.app/"

# List of available MP3 files
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

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Dropdown component
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
        self.vc.play(discord.FFmpegPCMAudio(mp3_url), after=lambda e: print(f"Finished: {e}"))
        await interaction.response.send_message(f"▶️ Playing: `{self.values[0]}`", ephemeral=True)

class SoundView(discord.ui.View):
    def __init__(self, vc):
        super().__init__()
        self.add_item(SoundSelect(vc))

# Bot events and commands
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@discord.app_commands.command(name="audibles", description="Play an MP3 from the dropdown")
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
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)

# Start bot
bot.run(TOKEN)
