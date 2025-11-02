import os
import io
import asyncio
import aiohttp
import subprocess
import urllib.parse
import discord
from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio, FFmpegOpusAudio, PCMVolumeTransformer

# --------------------
# ENV
# --------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID_RAW = os.getenv("GUILD_ID")
if not TOKEN or not GUILD_ID_RAW:
    raise RuntimeError("Missing DISCORD_BOT_TOKEN or GUILD_ID env var.")
GUILD_ID = int(GUILD_ID_RAW)

# Raw GitHub hosting base (no trailing slash)
BASE_URL = "https://raw.githubusercontent.com/Feralpossum/audibles_files/main/Audibles"

def _url_join(stem: str, ext: str) -> str:
    # URL-encode the filename (handles spaces and case exactly as on GitHub)
    fname = f"{stem}.{ext}"
    return f"{BASE_URL}/{urllib.parse.quote(fname)}"

# --------------------
# CATALOG
# For items with identical .mp3 and .mp4 stems, set mp3/mp4 to the same value.
# For items with mixed casing or spaces, set stems explicitly.
# --------------------
AUDIBLES = {
    # Original set
    "Boo":                  {"desc": "Classic jump scare",      "emoji": "🎃", "mp3": "Boo",                  "mp4": "Boo"},
    "DoneLosing":           {"desc": "Over it already",         "emoji": "🏁", "mp3": "DoneLosing",           "mp4": "DoneLosing"},
    "DontSlipMoppingFloor": {"desc": "Careful... it's wet!",    "emoji": "🧹", "mp3": "DontSlipMoppingFloor", "mp4": "DontSlipMoppingFloor"},
    "FatGuysNoMoney":       {"desc": "Hard relatable moment",   "emoji": "💸", "mp3": "FatGuysNoMoney",       "mp4": "FatGuysNoMoney"},
    "FromADrunkenMonkey":   {"desc": "Monkey mayhem",           "emoji": "🐒", "mp3": "FromADrunkenMonkey",   "mp4": "FromADrunkenMonkey"},
    "GreatestEVER":         {"desc": "All-time hype",           "emoji": "🏆", "mp3": "GreatestEVER",         "mp4": "GreatestEVER"},
    "INeverWinYouSuck":     {"desc": "Ultimate sore loser",     "emoji": "😡", "mp3": "INeverWinYouSuck",     "mp4": "INeverWinYouSuck"},
    "KeepPunching":         {"desc": "Fight back!",             "emoji": "🥊", "mp3": "KeepPunching",         "mp4": "KeepPunching"},
    # Repo shows "LovesmeLovesmeNot" (not "Lovesome...")
    "LovesmeLovesmeNot":    {"desc": "Love's a battlefield",    "emoji": "💔", "mp3": "LovesmeLovesmeNot",    "mp4": "LovesmeLovesmeNot"},
    # Repo has a space in filename: "Mmm roar"
    "Mmm roar":             {"desc": "Rawr means love",         "emoji": "🦁", "mp3": "Mmm roar",             "mp4": "Mmm roar"},
    "Mwahahaha":            {"desc": "Evil laugh",              "emoji": "😈", "mp3": "Mwahahaha",            "mp4": "Mwahahaha"},
    "NotEvenSameZipCodeFunny":{"desc": "You're not even close!", "emoji": "🏡", "mp3": "NotEvenSameZipCodeFunny","mp4":"NotEvenSameZipCodeFunny"},
    "Pleasestandstill":     {"desc": "Deer in headlights",      "emoji": "🦌", "mp3": "Pleasestandstill",     "mp4": "Pleasestandstill"},
    "ReallyLonelyBeingYou": {"desc": "A tragic roast",          "emoji": "😢", "mp3": "ReallyLonelyBeingYou", "mp4": "ReallyLonelyBeingYou"},
    "Sandwich":             {"desc": "Time for lunch",          "emoji": "🥪", "mp3": "Sandwich",             "mp4": "Sandwich"},
    "Score":                {"desc": "Winning!",                "emoji": "🏅", "mp3": "Score",                "mp4": "Score"},
    "SeriouslyEvenTrying":  {"desc": "Are you even trying?",    "emoji": "🤨", "mp3": "SeriouslyEvenTrying",  "mp4": "SeriouslyEvenTrying"},
    "ShakeLikeItDidntHurt": {"desc": "Shake it off",            "emoji": "🕺", "mp3": "ShakeLikeItDidntHurt", "mp4": "ShakeLikeItDidntHurt"},
    "WelcomeExpectingYou":  {"desc": "Grand entrance",          "emoji": "🎉", "mp3": "WelcomeExpectingYou",  "mp4": "WelcomeExpectingYou"},
    "Yawn":                 {"desc": "So bored",                "emoji": "🥱", "mp3": "Yawn",                 "mp4": "Yawn"},

    # New set (as per your repo listing)
    "Cheater":              {"desc": "Cheater",                 "emoji": "🔊", "mp3": "Cheater",              "mp4": "Cheater"},
    "Dude":                 {"desc": "Dude",                    "emoji": "🔊", "mp3": "Dude",                 "mp4": "Dude"},
    "FeelingTheBoring":     {"desc": "Feeling The Boring",      "emoji": "🔊", "mp3": "FeelingTheBoring",     "mp4": "FeelingTheBoring"},
    "GottaHurt":            {"desc": "Gotta Hurt",              "emoji": "🔊", "mp3": "GottaHurt",            "mp4": "GottaHurt"},
    "HelloICanSeeYou":      {"desc": "Hello I Can See You",     "emoji": "🔊", "mp3": "HelloICanSeeYou",      "mp4": "HelloICanSeeYou"},
    "Hilarious":            {"desc": "Hilarious",               "emoji": "🔊", "mp3": "Hilarious",            "mp4": "Hilarious"},
    # mp3 is "ItsOKImHere", mp4 is "ItsOkImHere" (case difference)
    "ItsOkImHere":          {"desc": "It's OK, I'm Here",       "emoji": "🔊", "mp3": "ItsOKImHere",          "mp4": "ItsOkImHere"},
    "MakemeHurtYou":        {"desc": "Make Me Hurt You",        "emoji": "🔊", "mp3": "MakemeHurtYou",        "mp4": "MakemeHurtYou"},
    "OhSnap":               {"desc": "Oh Snap",                 "emoji": "🔊", "mp3": "OhSnap",               "mp4": "OhSnap"},
    "OhYeah":               {"desc": "Oh Yeah",                 "emoji": "🔊", "mp3": "OhYeah",               "mp4": "OhYeah"},
    "Shower":               {"desc": "Shower",                  "emoji": "🔊", "mp3": "Shower",               "mp4": "Shower"},
    "SockInIt":             {"desc": "Sock In It",              "emoji": "🔊", "mp3": "SockInIt",             "mp4": "SockInIt"},
    "Spew":                 {"desc": "Spew",                    "emoji": "🔊", "mp3": "Spew",                 "mp4": "Spew"},
    "StickYaDone":          {"desc": "Stick Ya Done",           "emoji": "🔊", "mp3": "StickYaDone",          "mp4": "StickYaDone"},
    "TalkToHand":           {"desc": "Talk To Hand",            "emoji": "🔊", "mp3": "TalkToHand",           "mp4": "TalkToHand"},
    "Unplug":               {"desc": "Unplug",                  "emoji": "🔊", "mp3": "Unplug",               "mp4": "Unplug"},
    "WhaddUP":              {"desc": "Whadd Up",                "emoji": "🔊", "mp3": "WhaddUP",              "mp4": "WhaddUP"},
    "Whine":                {"desc": "Whine",                   "emoji": "🔊", "mp3": "Whine",                "mp4": "Whine"},
    "Whistle":              {"desc": "Whistle",                 "emoji": "🔊", "mp3": "Whistle",              "mp4": "Whistle"},
    "YouCrying":            {"desc": "You Crying",              "emoji": "🔊", "mp3": "YouCrying",            "mp4": "YouCrying"},
    "YouSuckMore":          {"desc": "You Suck More",           "emoji": "🔊", "mp3": "YouSuckMore",          "mp4": "YouSuckMore"},
    "nananana":             {"desc": "Nananana",                "emoji": "🔊", "mp3": "nananana",             "mp4": "nananana"},
    "bye_bye":              {"desc": "Bye Bye Now",             "emoji": "🔊", "mp3": "bye_bye",              "mp4": "bye_bye"},
}

# --------------------
# Bot setup
# --------------------
intents = discord.Intents.default()
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --------------------
# Helpers for resilient voice playback
# --------------------
async def _cleanup_voice(guild: discord.Guild):
    vc = guild.voice_client
    if vc:
        try:
            await vc.disconnect(force=True)
        except Exception:
            pass
        await asyncio.sleep(0.5)

async def _connect_voice_strong(channel: discord.VoiceChannel, attempts: int = 5) -> discord.VoiceClient:
    last = None
    for i in range(1, attempts + 1):
        try:
            return await channel.connect(timeout=25.0, reconnect=True, self_deaf=True)
        except Exception as e:
            last = e
            await asyncio.sleep(i)  # backoff 1,2,3,4,5s
    raise last

async def _play_audio_in_vc(interaction: discord.Interaction, name: str):
    info = AUDIBLES.get(name)
    if not info:
        await interaction.followup.send("❌ Unknown audible.", ephemeral=True)
        return

    # Ensure user in voice channel
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.followup.send("❌ Join a voice channel first.", ephemeral=True)
        return

    # Clean stale VC, then connect with retries (handles 4006 invalid session)
    await _cleanup_voice(interaction.guild)
    try:
        vc = await _connect_voice_strong(interaction.user.voice.channel)
    except Exception as e:
        await interaction.followup.send(f"❌ Can’t connect to voice: {e}", ephemeral=True)
        return

    mp3_url = _url_join(info["mp3"], "mp3")

    # Try robust recommended path first
    try:
        source = await FFmpegOpusAudio.from_probe(
            mp3_url,
            method="fallback",
            executable="ffmpeg",
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin",
            options="-vn"
        )
        vc.play(PCMVolumeTransformer(source, volume=1.0))
    except Exception as first_err:
        # Fallback: download bytes and pipe via ffmpeg
        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(mp3_url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status != 200:
                        await interaction.followup.send(f"⚠️ Audio unavailable (HTTP {resp.status})", ephemeral=True)
                        await _cleanup_voice(interaction.guild)
                        return
                    audio_bytes = await resp.read()
            buf = io.BytesIO(audio_bytes); buf.seek(0)

            cmd = [
                "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
                "-i", "pipe:0", "-vn", "-f", "s16le", "-ar", "48000", "-ac", "2", "pipe:1"
            ]
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                proc.stdin.write(buf.getbuffer())
                proc.stdin.close()
            except Exception:
                pass

            raw = FFmpegPCMAudio(proc.stdout)
            vc.play(PCMVolumeTransformer(raw, volume=1.0))
        except Exception as second_err:
            await interaction.followup.send(f"❌ Couldn’t start audio: {first_err} / fallback: {second_err}", ephemeral=True)
            await _cleanup_voice(interaction.guild)
            return

    # Wait for start (if gateway was flaky, one reconnect/replay attempt)
    started = False
    for _ in range(20):  # ~10s
        if vc.is_playing():
            started = True
            break
        await asyncio.sleep(0.5)

    if not started:
        await _cleanup_voice(interaction.guild)
        try:
            vc = await _connect_voice_strong(interaction.user.voice.channel)
            source = await FFmpegOpusAudio.from_probe(
                mp3_url,
                method="fallback",
                executable="ffmpeg",
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin",
                options="-vn"
            )
            vc.play(PCMVolumeTransformer(source, volume=1.0))
        except Exception as e:
            await interaction.followup.send(f"⚠️ Audio didn’t start after retry: {e}", ephemeral=True)
            await _cleanup_voice(interaction.guild)
            return

    # Drain until finished; then disconnect
    while vc.is_playing():
        await asyncio.sleep(0.5)
    await _cleanup_voice(interaction.guild)

# --------------------
# Autocomplete
# --------------------
async def audible_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    current_l = (current or "").lower()
    matches = []
    for display_name, meta in AUDIBLES.items():
        if (current_l in display_name.lower()) or (current_l in meta["desc"].lower()):
            label = f"{display_name} {meta['emoji']} – {meta['desc']}"
            # Discord option label must be <=100 chars; value <=100 as well
            matches.append(app_commands.Choice(name=label[:100], value=display_name[:100]))
        if len(matches) >= 25:
            break
    # If no match or user typed nothing, return first 25
    if not matches:
        for display_name, meta in list(AUDIBLES.items())[:25]:
            label = f"{display_name} {meta['emoji']} – {meta['desc']}"
            matches.append(app_commands.Choice(name=label[:100], value=display_name[:100]))
    return matches[:25]

# --------------------
# Events & Commands
# --------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

@bot.tree.command(name="audible", description="Send the visual and autoplay the sound", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(name="Start typing to search")
@app_commands.autocomplete(name=audible_autocomplete)
async def audible(interaction: discord.Interaction, name: str):
    meta = AUDIBLES.get(name)
    if not meta:
        await interaction.response.send_message("❌ Unknown audible.", ephemeral=True)
        return

    # Defer to allow fetch time
    await interaction.response.defer()

    # 1) Send MP4 visual (best-effort)
    mp4_url = _url_join(meta["mp4"], "mp4")
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(mp4_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    buf = io.BytesIO(await resp.read())
                    await interaction.followup.send(file=discord.File(buf, filename=f"{meta['mp4']}.mp4"))
                else:
                    await interaction.followup.send(f"⚠️ Video unavailable (HTTP {resp.status})")
    except Exception as e:
        await interaction.followup.send(f"⚠️ Visual error: {e}")

    # 2) Join VC & autoplay MP3
    await _play_audio_in_vc(interaction, name)

# --------------------
# Run
# --------------------
bot.run(TOKEN)
