import os
import io
import asyncio
import aiohttp
import discord
from discord.ext import commands
from discord.ui import Select, View
from discord import FFmpegPCMAudio, PCMVolumeTransformer

# Load your bot token and guild ID from environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

# Raw GitHub URL for your hosted audibles
BASE_URL = "https://raw.githubusercontent.com/Feralpossum/audibles_files/main/Audibles"

# The list of audibles with descriptions and emojis
AUDIBLES = {
    "Boo":                  {"description": "Classic jump scare",     "emoji": "🎃"},
    "DoneLosing":           {"description": "Over it already",       "emoji": "🏁"},
    "DontSlipMoppingFloor": {"description": "Careful... it's wet!", "emoji": "🧹"},
    "FatGuysNoMoney":       {"description": "Hard relatable moment","emoji": "💸"},
    "FromADrunkenMonkey":   {"description": "Monkey mayhem",         "emoji": "🐒"},
    "GreatestEVER":         {"description": "All-time hype",         "emoji": "🏆"},
    "INeverWinYouSuck":     {"description": "Ultimate sore loser",  "emoji": "😡"},
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
    # New audibles
    "Cheater":              {"description": "Cheater",               "emoji": "🔊"},
    "Dude":                 {"description": "Dude",                  "emoji": "😎"},
    "FeelingTheBoring":     {"description": "Feeling the boring",    "emoji": "😴"},
    "GottaHurt":            {"description": "Gotta hurt",            "emoji": "😖"},
    "HelloICanSeeYou":      {"description": "Hello I can see you",   "emoji": "👀"},
    "Hilarious":            {"description": "Hilarious",             "emoji": "😂"},
    "ItsOkImHere":          {"description": "It's OK I'm here",      "emoji": "👌"},
    "MakemeHurtYou":        {"description": "Make me hurt you",      "emoji": "😈"},
    "Mmm roar":             {"description": "Mmm roar",              "emoji": "🐯"},
    "OhSnap":               {"description": "Oh snap",               "emoji": "💥"},
    "OhYeah":               {"description": "Oh yeah",               "emoji": "👍"},
    "Shower":               {"description": "Shower",                "emoji": "🚿"},
    "SockInIt":             {"description": "Sock in it",            "emoji": "🧦"},
    "Spew":                 {"description": "Spew",                  "emoji": "🤢"},
    "StickYaDone":          {"description": "Stick ya done",         "emoji": "🥒"},
    "TalkToHand":           {"description": "Talk to hand",          "emoji": "✋"},
    "Unplug":               {"description": "Unplug",                "emoji": "🔌"},
    "WhaddUP":              {"description": "Whadd up",              "emoji": "👋"},
    "Whine":                {"description": "Whine",                 "emoji": "😩"},
    "Whistle":              {"description": "Whistle",               "emoji": "😗"},
    "YouSuckMore":          {"description": "You suck more",         "emoji": "😈"},
    "nananana":             {"description": "Nananana",              "emoji": "🎵"},
}

# Create bot with voice intent enabled
intents = discord.Intents.default()
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

class AudibleSelect(Select):
    def __init__(self):
        super().__init__(
            placeholder="Select an audible…",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label=name,
                    description=data["description"],
                    emoji=data["emoji"]
                ) for name, data in AUDIBLES.items()
            ]
        )

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        mp4_url = f"{BASE_URL}/{choice}.mp4"
        mp3_url = f"{BASE_URL}/{choice}.mp3"

        # Acknowledge so we have time to fetch
        await interaction.response.defer()

        # 1) Send MP4 visual (will autoplay muted)
        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(mp4_url) as resp:
                    if resp.status == 200:
                        buffer = io.BytesIO(await resp.read())
                        await interaction.followup.send(
                            file=discord.File(buffer, filename=f"{choice}.mp4")
                        )
                    else:
                        await interaction.followup.send(
                            f"⚠️ Couldn’t fetch video for **{choice}** (HTTP {resp.status})"
                        )
        except Exception as e:
            await interaction.followup.send(f"❌ Video fetch error: {e}")

        # 2) Join voice channel & autoplay MP3
        if interaction.user.voice and interaction.user.voice.channel:
            vc = interaction.guild.voice_client or await interaction.user.voice.channel.connect()
            try:
                ffmpeg_opts = {
                    "executable": "ffmpeg",
                    "before_options": "-re -nostdin",
                    "options": "-vn"
                }
                source = PCMVolumeTransformer(
                    FFmpegPCMAudio(mp3_url, **ffmpeg_opts)
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
        print(f"❌ Slash command sync failed: {e}")

@bot.tree.command(
    name="audibles",
    description="Play an audible from the list",
    guild=discord.Object(id=GUILD_ID)
)
async def audibles(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Choose an audible to play:", view=AudibleView(), ephemeral=True
    )

bot.run(TOKEN)
