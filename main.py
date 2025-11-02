import os
import io
import asyncio
import urllib.parse
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio, PCMVolumeTransformer

# --- Environment ---
TOKEN    = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

BASE_URL = "https://raw.githubusercontent.com/Feralpossum/audibles_files/main/Audibles"

# --- Try to load Opus early; if this fails you'll connect but never hear audio ---
try:
    if not discord.opus.is_loaded():
        discord.opus.load_opus("libopus.so.0")  # Debian/Ubuntu soname
    print("✅ Opus loaded:", discord.opus.is_loaded())
except Exception as e:
    print("❌ Failed to load Opus (libopus). Voice will not play audio:", e)

# --- Audibles (keep your full set here) ---
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

    # New audibles (sample of what you listed; add the rest as needed)
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
    "bye_bye":              {"description": "Bye Bye Now",            "emoji": "🔊"},
}

# --- Bot setup ---
intents = discord.Intents.default()
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Per-guild lock so we never double-connect or overlap voice sessions
_voice_locks: dict[int, asyncio.Lock] = {}

def guild_lock(guild_id: int) -> asyncio.Lock:
    if guild_id not in _voice_locks:
        _voice_locks[guild_id] = asyncio.Lock()
    return _voice_locks[guild_id]

# --- Autocomplete for large lists (Discord UI limit: 25 items in menus) ---
async def audible_autocomplete(interaction: discord.Interaction, current: str):
    current_lower = current.lower()
    names = [n for n in AUDIBLES if current_lower in n.lower()]
    names.sort()
    return [app_commands.Choice(name=n, value=n) for n in names[:25]]

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

@bot.tree.command(name="audible", description="Post visual & autoplay audio", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(name="Start typing to search audibles")
@app_commands.autocomplete(name=audible_autocomplete)
async def audible(interaction: discord.Interaction, name: str):
    # Encode name for URLs (handles spaces like 'Mmm roar' -> 'Mmm%20roar')
    safe = urllib.parse.quote(name)

    mp4_url = f"{BASE_URL}/{safe}.mp4"
    mp3_url = f"{BASE_URL}/{safe}.mp3"

    await interaction.response.defer()

    # 1) Post MP4 in text channel (visual autoplay muted in Discord UI)
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(mp4_url) as resp:
                if resp.status == 200:
                    buf = io.BytesIO(await resp.read())
                    await interaction.followup.send(file=discord.File(buf, filename=f"{name}.mp4"))
                else:
                    await interaction.followup.send(f"⚠️ Video unavailable for **{name}** (HTTP {resp.status})")
    except Exception as e:
        await interaction.followup.send(f"❌ Visual fetch error: {e}")

    # 2) Join VC & play MP3 (guarded by a per-guild lock)
    if not (interaction.user.voice and interaction.user.voice.channel):
        return  # nothing else to do

    lock = guild_lock(interaction.guild.id)
    async with lock:
        # If a stale VC exists, drop it first
        if interaction.guild.voice_client:
            try:
                await interaction.guild.voice_client.disconnect(force=True)
            except Exception:
                pass
            await asyncio.sleep(0.25)

        # Fresh connect (avoid reconnect loops)
        try:
            vc = await interaction.user.voice.channel.connect(
                timeout=10,
                reconnect=False,
                self_deaf=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Voice connect failed: {e}")
            return

        # Ensure Opus is available before trying to play
        if not discord.opus.is_loaded():
            await interaction.followup.send("❌ Opus codec not loaded on server. Audio cannot be sent.")
            try:
                await vc.disconnect(force=True)
            finally:
                return

        try:
            ffmpeg_kwargs = {
                "executable": "ffmpeg",
                "before_options": "-nostdin -re",
                "options": "-vn -ac 2 -ar 48000"
            }
            source = PCMVolumeTransformer(FFmpegPCMAudio(mp3_url, **ffmpeg_kwargs), volume=1.0)
            vc.play(source)

            # Wait until done (or force stop after 20s as a guard)
            for _ in range(200):  # 200 * 0.1s = 20s
                if not vc.is_playing():
                    break
                await asyncio.sleep(0.1)
        except Exception as e:
            await interaction.followup.send(f"❌ Playback error: {e}")
        finally:
            try:
                await vc.disconnect(force=True)
            except Exception:
                pass

# --- Run ---
bot.run(TOKEN)
