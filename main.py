import os
import io
import asyncio
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio, PCMVolumeTransformer

# Load your bot token and guild ID from environment variables
TOKEN    = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

# Base URL for your raw GitHub–hosted audibles
BASE_URL = "https://raw.githubusercontent.com/Feralpossum/audibles_files/main/Audibles"

# All audibles with descriptions and emojis
AUDIBLES = {
    # Original audibles
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
    "NotEvenSameZipCodeFunny": {"description": "You're not even close!", "emoji": "🏡"},
    "Pleasestandstill":     {"description": "Deer in headlights",    "emoji": "🦌"},
    "ReallyLonelyBeingYou":{"description": "A tragic roast",       "emoji": "😢"},
    "Sandwich":             {"description": "Time for lunch",        "emoji": "🥪"},
    "Score":                {"description": "Winning!",              "emoji": "🏅"},
    "SeriouslyEvenTrying":  {"description": "Are you even trying?", "emoji": "🤨"},
    "ShakeLikeItDidntHurt": {"description": "Shake it off",          "emoji": "🕺"},
    "WelcomeExpectingYou":  {"description": "Grand entrance",        "emoji": "🎉"},
    "Yawn":                 {"description": "So bored",              "emoji": "🥱"},

    # New audibles
    "Cheater":              {"description": "Cheater",               "emoji": "🔊"},
    "Dude":                 {"description": "Dude",                  "emoji": "🔊"},
    "FeelingTheBoring":     {"description": "Feeling The Boring",    "emoji": "🔊"},
    "GottaHurt":            {"description": "Gotta Hurt",            "emoji": "🔊"},
    "HelloICanSeeYou":      {"description": "Hello I Can See You",   "emoji": "🔊"},
    "Hilarious":            {"description": "Hilarious",             "emoji": "🔊"},
    "ItsOkImHere":          {"description": "It's OK, I'm Here",     "emoji": "🔊"},
    "MakemeHurtYou":        {"description": "Make Me Hurt You",      "emoji": "🔊"},
    "Mmm roar":             {"description": "Mmm roar",              "emoji": "🔊"},
    "OhSnap":               {"description": "Oh Snap",               "emoji": "🔊"},
    "OhYeah":               {"description": "Oh Yeah",               "emoji": "🔊"},
    "Shower":               {"description": "Shower",                "emoji": "🔊"},
    "SockInIt":             {"description": "Sock In It",            "emoji": "🔊"},
    "Spew":                 {"description": "Spew",                  "emoji": "🔊"},
    "StickYaDone":          {"description": "Stick Ya Done",         "emoji": "🔊"},
    "TalkToHand":           {"description": "Talk To Hand",          "emoji": "🔊"},
    "Unplug":               {"description": "Unplug",                "emoji": "🔊"},
    "WhaddUP":              {"description": "Whadd Up",              "emoji": "🔊"},
    "Whine":                {"description": "Whine",                 "emoji": "🔊"},
    "Whistle":              {"description": "Whistle",               "emoji": "🔊"},
    "YouCrying":            {"description": "You Crying",            "emoji": "🔊"},
    "YouSuckMore":          {"description": "You Suck More",         "emoji": "🔊"},
    "nananana":             {"description": "Nananana",              "emoji": "🔊"},
    "bye_bye":             {"description": "Bye Bye Now",            "emoji": "🔊"},
}

# Bot setup
intents = discord.Intents.default()
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def audible_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> list[app_commands.Choice[str]]:
    choices = [
        app_commands.Choice(name=name, value=name)
        for name in AUDIBLES
        if current.lower() in name.lower()
    ]
    return choices[:25]

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

@bot.tree.command(
    name="audible",
    description="Play an audible from the list",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(name="Start typing to search audibles")
@app_commands.autocomplete(name=audible_autocomplete)
async def audible(
    interaction: discord.Interaction,
    name: str
):
    # Construct URLs
    mp4_url = f"{BASE_URL}/{name}.mp4"
    mp3_url = f"{BASE_URL}/{name}.mp3"

    # Defer to allow fetch time
    await interaction.response.defer()

    # 1) Send MP4 visual
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(mp4_url) as resp:
                if resp.status == 200:
                    buffer = io.BytesIO(await resp.read())
                    await interaction.followup.send(
                        file=discord.File(buffer, filename=f"{name}.mp4")
                    )
                else:
                    await interaction.followup.send(
                        f"⚠️ Video unavailable (HTTP {resp.status})"
                    )
    except Exception as e:
        await interaction.followup.send(f"❌ Visual error: {e}")

    # 2) Join VC & autoplay MP3
    if interaction.user.voice and interaction.user.voice.channel:
        vc = interaction.guild.voice_client or await interaction.user.voice.channel.connect()
        try:
            ff_opts = {
                "executable": "ffmpeg",
                "before_options": "-re -nostdin",
                "options": "-vn"
            }
            source = PCMVolumeTransformer(
                FFmpegPCMAudio(mp3_url, **ff_opts)
            )
            vc.play(source)
            while vc.is_playing():
                await asyncio.sleep(1)
            await vc.disconnect()
        except Exception as e:
            await interaction.followup.send(f"❌ Playback error: {e}")

bot.run(TOKEN)
