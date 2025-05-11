import discord
from discord.ext import commands
from discord.ui import Select, View
import asyncio
import os
import aiohttp
import io

# Load token and guild ID from environment
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

# Base URL pointing to your raw GitHub repository files
BASE_URL = "https://raw.githubusercontent.com/Feralpossum/audibles_files/main/Audibles"

# Define your audibles with descriptions and emojis
AUDIBLES = {
    "Boo":                  {"description": "Classic jump scare",     "emoji": "🎃"},
    "DoneLosing":           {"description": "Over it already",       "emoji": "🏁"},
    "DontSlipMoppingFloor": {"description": "Careful... it's wet!", "emoji": "🧹"},
    "FatGuysNoMoney":       {"description": "Hard relatable moment", "emoji": "💸"},
    "FromADrunkenMonkey":   {"description": "Monkey mayhem",         "emoji": "🐒"},
    "GreatestEVER":         {"description": "All-time hype",         "emoji": "🏆"},
    "INeverWinYouSuck":     {"description": "Ultimate sore loser",   "emoji": "😡"},
    "KeepPunching":         {"description": "Fight back!",           "emoji": "🥊"},
    "LovesomeLovesomeNot":  {"description": "Love's a battlefield",  "emoji": "💔"},
    "Mmm_roar":             {"description": "Rawr means love",       "emoji": "🦁"},
    "Mwahahaha":            {"description": "Evil laugh",            "emoji": "😈"},
    "NotEvenSameZipCodeFunny": {"description":"You're not even close!","emoji":"🏡"},
    "Pleasestandstill":     {"description": "Deer in headlights",    "emoji": "🦌"},
    "ReallyLonelyBeingYou": {"description": "A tragic roast",       "emoji": "😢"},
    "Sandwich":             {"description": "Time for lunch",        "emoji": "🥪"},
    "Score":                {"description": "Winning!",              "emoji": "🏅"},
    "SeriouslyEvenTrying":  {"description": "Are you even trying?", "emoji": "🤨"},
    "ShakeLikeItDidntHurt": {"description": "Shake it off",          "emoji": "🕺"},
    "WelcomeExpectingYou":  {"description": "Grand entrance",        "emoji": "🎉"},
    "Yawn":                 {"description": "So bored",              "emoji": "🥱"},
}

# Create bot with voice intent
intents = discord.Intents.default()
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

class AudibleSelect(Select):
    def __init__(self):
        super().__init__(
            placeholder="Select an audible...",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label=name, description=data["description"], emoji=data["emoji"])
                for name, data in AUDIBLES.items()
            ]
        )

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        mp4_url = f"{BASE_URL}/{choice}.mp4"
        mp3_url = f"{BASE_URL}/{choice}.mp3"

        # Acknowledge the interaction
        await interaction.response.defer()

        # Send MP4 visual to chat
        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(mp4_url) as resp:
                    if resp.status == 200:
                        buf = io.BytesIO(await resp.read())
                        await interaction.followup.send(
                            file=discord.File(buf, filename=f"{choice}.mp4")
                        )
                    else:
                        await interaction.followup.send(
                            f"⚠️ MP4 unavailable (HTTP {resp.status})"
                        )
        except Exception as e:
            await interaction.followup.send(f"❌ Error fetching MP4: {e}")

        # Play MP3 in voice channel
        if interaction.user.voice and interaction.user.voice.channel:
            vc = interaction.guild.voice_client or await interaction.user.voice.channel.connect()
            try:
                source = discord.FFmpegPCMAudio(
                    mp3_url,
                    executable="ffmpeg",
                    before_options="-re"
                )
                vc.play(source)
                while vc.is_playing():
                    await asyncio.sleep(1)
                await vc.disconnect()
            except Exception as e:
                await interaction.followup.send(f"❌ Voice playback error: {e}")

class AudibleView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(AudibleSelect())

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

@bot.tree.command(
    name="audibles",
    description="Play an audible from the list",
    guild=discord.Object(id=GUILD_ID)
)
async def audibles(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Choose an audible to play:",
        view=AudibleView(),
        ephemeral=True
    )

bot.run(TOKEN)
