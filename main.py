# main.py  (FFmpeg-only, no Lavalink)
import os
import io
import asyncio
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio, PCMVolumeTransformer

# ========= ENV =========
TOKEN    = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))

# Raw GitHub URL for your hosted audibles
BASE_URL = "https://raw.githubusercontent.com/Feralpossum/audibles_files/main/Audibles"

# ========= AUDIBLES (full list) =========
AUDIBLES = {
    # Originals
    "Boo":                  {"description": "Classic jump scare",     "emoji": "🎃"},
    "DoneLosing":           {"description": "Over it already",        "emoji": "🏁"},
    "DontSlipMoppingFloor": {"description": "Careful... it's wet!",   "emoji": "🧹"},
    "FatGuysNoMoney":       {"description": "Hard relatable moment",  "emoji": "💸"},
    "FromADrunkenMonkey":   {"description": "Monkey mayhem",          "emoji": "🐒"},
    "GreatestEVER":         {"description": "All-time hype",          "emoji": "🏆"},
    "INeverWinYouSuck":     {"description": "Ultimate sore loser",    "emoji": "😡"},
    "KeepPunching":         {"description": "Fight back!",            "emoji": "🥊"},
    "LovesomeLovesomeNot":  {"description": "Love's a battlefield",   "emoji": "💔"},
    "Mmm_roar":             {"description": "Rawr means love",        "emoji": "🦁"},
    "Mwahahaha":            {"description": "Evil laugh",             "emoji": "😈"},
    "NotEvenSameZipCodeFunny": {"description": "You're not even close!", "emoji": "🏡"},
    "Pleasestandstill":     {"description": "Deer in headlights",     "emoji": "🦌"},
    "ReallyLonelyBeingYou": {"description": "A tragic roast",         "emoji": "😢"},
    "Sandwich":             {"description": "Time for lunch",         "emoji": "🥪"},
    "Score":                {"description": "Winning!",               "emoji": "🏅"},
    "SeriouslyEvenTrying":  {"description": "Are you even trying?",   "emoji": "🤨"},
    "ShakeLikeItDidntHurt": {"description": "Shake it off",           "emoji": "🕺"},
    "WelcomeExpectingYou":  {"description": "Grand entrance",         "emoji": "🎉"},
    "Yawn":                 {"description": "So bored",               "emoji": "🥱"},

    # New batch
    "Cheater":              {"description": "Cheater",                "emoji": "🔊"},
    "Dude":                 {"description": "Dude",                   "emoji": "🔊"},
    "FeelingTheBoring":     {"description": "Feeling The Boring",     "emoji": "🔊"},
    "GottaHurt":            {"description": "Gotta Hurt",             "emoji": "🔊"},
    "HelloICanSeeYou":      {"description": "Hello I Can See You",    "emoji": "🔊"},
    "Hilarious":            {"description": "Hilarious",              "emoji": "🔊"},
    "ItsOkImHere":          {"description": "It's OK, I'm Here",      "emoji": "🔊"},
    "MakemeHurtYou":        {"description": "Make Me Hurt You",       "emoji": "🔊"},
    "Mmm roar":             {"description": "Mmm roar",               "emoji": "🔊"},
    "OhSnap":               {"description": "Oh Snap",                "emoji": "🔊"},
    "OhYeah":               {"description": "Oh Yeah",                "emoji": "🔊"},
    "Shower":               {"description": "Shower",                 "emoji": "🔊"},
    "SockInIt":             {"description": "Sock In It",             "emoji": "🔊"},
    "Spew":                 {"description": "Spew",                   "emoji": "🔊"},
    "StickYaDone":          {"description": "Stick Ya Done",          "emoji": "🔊"},
    "TalkToHand":           {"description": "Talk To Hand",           "emoji": "🔊"},
    "Unplug":               {"description": "Unplug",                 "emoji": "🔊"},
    "WhaddUP":              {"description": "Whadd Up",               "emoji": "🔊"},
    "Whine":                {"description": "Whine",                  "emoji": "🔊"},
    "Whistle":              {"description": "Whistle",                "emoji": "🔊"},
    "YouCrying":            {"description": "You Crying",             "emoji": "🔊"},
    "YouSuckMore":          {"description": "You Suck More",          "emoji": "🔊"},
    "nananana":             {"description": "Nananana",               "emoji": "🔊"},
    "ByeByeNow":              {"description": "Bye Bye Now",            "emoji": "🔊"},
}

# ========= BOT =========
intents = discord.Intents.default()
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---- helpers ----
def mp_urls(name: str) -> tuple[str, str]:
    return (f"{BASE_URL}/{name}.mp4", f"{BASE_URL}/{name}.mp3")

async def audible_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=k, value=k)
        for k in AUDIBLES.keys()
        if current.lower() in k.lower()
    ][:25]

async def send_visual(interaction: discord.Interaction, mp4_url: str, name: str):
    """Send the MP4 file to the text channel."""
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(mp4_url) as resp:
                if resp.status == 200:
                    buf = io.BytesIO(await resp.read())
                    await interaction.followup.send(file=discord.File(buf, filename=f"{name}.mp4"))
                else:
                    await interaction.followup.send(f"⚠️ Video unavailable (HTTP {resp.status})")
    except Exception as e:
        await interaction.followup.send(f"❌ Visual fetch error: {e}")

async def play_via_ffmpeg(interaction: discord.Interaction, name: str, mp3_url: str):
    """Join user's VC, stream MP3 from GitHub Raw via ffmpeg, then disconnect."""
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.followup.send("❌ You need to be in a voice channel.")
        return

    # Connect or reuse
    vc: discord.VoiceClient = interaction.guild.voice_client  # type: ignore
    if not vc or not vc.is_connected():
        try:
            vc = await interaction.user.voice.channel.connect(timeout=10.0, reconnect=False)
        except Exception as e:
            await interaction.followup.send(f"❌ Can’t connect to voice: {e}")
            return

    ffmpeg_opts = {
        # Debian ffmpeg in container
        "executable": "ffmpeg",
        # Robust reconnect for HTTP streaming from GitHub Raw
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin",
        "options": "-vn",
    }

    try:
        source = PCMVolumeTransformer(FFmpegPCMAudio(mp3_url, **ffmpeg_opts))
        vc.play(source)

        # Wait until finished
        while vc.is_playing():
            await asyncio.sleep(0.5)
    except Exception as e:
        await interaction.followup.send(f"❌ Playback error: {e}")
    finally:
        try:
            await vc.disconnect(force=True)
        except Exception:
            pass

# ========= EVENTS / COMMANDS =========
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Slash sync failed: {e}")

@bot.tree.command(
    name="audible",
    description="Send the video and autoplay the matching sound in voice",
    guild=discord.Object(id=GUILD_ID),
)
@app_commands.describe(name="Start typing to search audibles")
@app_commands.autocomplete(name=audible_autocomplete)
async def audible(interaction: discord.Interaction, name: str):
    if name not in AUDIBLES:
        await interaction.response.send_message("❌ Unknown audible.", ephemeral=True)
        return

    mp4_url, mp3_url = mp_urls(name)
    await interaction.response.defer()

    # 1) Post the MP4 visual in the text channel
    await send_visual(interaction, mp4_url, name)

    # 2) Join voice & play MP3
    await play_via_ffmpeg(interaction, name, mp3_url)

# ========= RUN =========
if not TOKEN or not GUILD_ID:
    raise SystemExit("DISCORD_BOT_TOKEN and GUILD_ID must be set")
bot.run(TOKEN)
