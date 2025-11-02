import os
import io
import asyncio
import urllib.parse
import aiohttp
import contextlib
import discord
from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio, PCMVolumeTransformer

# === Environment ===
TOKEN    = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
BASE_URL = "https://raw.githubusercontent.com/Feralpossum/audibles_files/main/Audibles"

# === Load Opus ===
try:
    if not discord.opus.is_loaded():
        discord.opus.load_opus("libopus.so.0")
    print("✅ Opus loaded:", discord.opus.is_loaded())
except Exception as e:
    print("❌ Opus failed to load:", e)

# === Audio List ===
AUDIBLES = {
    "Boo": {"description": "Classic jump scare", "emoji": "🎃"},
    "DoneLosing": {"description": "Over it already", "emoji": "🏁"},
    "DontSlipMoppingFloor": {"description": "Careful... it's wet!", "emoji": "🧹"},
    "FatGuysNoMoney": {"description": "Hard relatable moment", "emoji": "💸"},
    "FromADrunkenMonkey": {"description": "Monkey mayhem", "emoji": "🐒"},
    "GreatestEVER": {"description": "All-time hype", "emoji": "🏆"},
    "INeverWinYouSuck": {"description": "Ultimate sore loser", "emoji": "😡"},
    "KeepPunching": {"description": "Fight back!", "emoji": "🥊"},
    "LovesomeLovesomeNot": {"description": "Love's a battlefield", "emoji": "💔"},
    "Mmm_roar": {"description": "Rawr means love", "emoji": "🦁"},
    "Mwahahaha": {"description": "Evil laugh", "emoji": "😈"},
    "NotEvenSameZipCodeFunny": {"description": "You're not even close!", "emoji": "🏡"},
    "Pleasestandstill": {"description": "Deer in headlights", "emoji": "🦌"},
    "ReallyLonelyBeingYou": {"description": "A tragic roast", "emoji": "😢"},
    "Sandwich": {"description": "Time for lunch", "emoji": "🥪"},
    "Score": {"description": "Winning!", "emoji": "🏅"},
    "SeriouslyEvenTrying": {"description": "Are you even trying?", "emoji": "🤨"},
    "ShakeLikeItDidntHurt": {"description": "Shake it off", "emoji": "🕺"},
    "WelcomeExpectingYou": {"description": "Grand entrance", "emoji": "🎉"},
    "Yawn": {"description": "So bored", "emoji": "🥱"},
    # Newer audibles
    "Cheater": {"description": "Cheater", "emoji": "🔊"},
    "Dude": {"description": "Dude", "emoji": "🔊"},
    "FeelingTheBoring": {"description": "Feeling The Boring", "emoji": "🔊"},
    "GottaHurt": {"description": "Gotta Hurt", "emoji": "🔊"},
    "HelloICanSeeYou": {"description": "Hello I Can See You", "emoji": "🔊"},
    "Hilarious": {"description": "Hilarious", "emoji": "🔊"},
    "ItsOkImHere": {"description": "It's OK, I'm Here", "emoji": "🔊"},
    "MakemeHurtYou": {"description": "Make Me Hurt You", "emoji": "🔊"},
    "OhSnap": {"description": "Oh Snap", "emoji": "🔊"},
    "OhYeah": {"description": "Oh Yeah", "emoji": "🔊"},
    "Shower": {"description": "Shower", "emoji": "🔊"},
    "SockInIt": {"description": "Sock In It", "emoji": "🔊"},
    "Spew": {"description": "Spew", "emoji": "🔊"},
    "StickYaDone": {"description": "Stick Ya Done", "emoji": "🔊"},
    "TalkToHand": {"description": "Talk To Hand", "emoji": "🔊"},
    "Unplug": {"description": "Unplug", "emoji": "🔊"},
    "WhaddUP": {"description": "Whadd Up", "emoji": "🔊"},
    "Whine": {"description": "Whine", "emoji": "🔊"},
    "Whistle": {"description": "Whistle", "emoji": "🔊"},
    "YouCrying": {"description": "You Crying", "emoji": "🔊"},
    "YouSuckMore": {"description": "You Suck More", "emoji": "🔊"},
    "nananana": {"description": "Nananana", "emoji": "🔊"},
    "bye_bye": {"description": "Bye Bye Now", "emoji": "🔊"},
}

# === Bot Setup ===
intents = discord.Intents.default()
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)
_voice_locks: dict[int, asyncio.Lock] = {}


def guild_lock(guild_id: int):
    if guild_id not in _voice_locks:
        _voice_locks[guild_id] = asyncio.Lock()
    return _voice_locks[guild_id]


# === Voice Helpers ===
async def safe_disconnect(guild: discord.Guild):
    vc = guild.voice_client
    if vc:
        with contextlib.suppress(Exception):
            if vc.is_playing():
                vc.stop()
        with contextlib.suppress(Exception):
            await vc.disconnect(force=True)


async def connect_vc(channel: discord.VoiceChannel, max_tries=5):
    await safe_disconnect(channel.guild)
    delay = 1
    last_exc = None
    for attempt in range(1, max_tries + 1):
        try:
            vc = await channel.connect(timeout=15, reconnect=False, self_deaf=False)
            return vc
        except Exception as e:
            last_exc = e
            await asyncio.sleep(delay)
            delay = min(delay * 2, 10)
    raise last_exc


def ffmpeg_opts_for_http_stream():
    return {
        "executable": "ffmpeg",
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin",
        "options": "-vn -ac 2 -ar 48000"
    }


async def play_mp3(vc: discord.VoiceClient, url: str):
    src = PCMVolumeTransformer(FFmpegPCMAudio(url, **ffmpeg_opts_for_http_stream()), volume=1.0)
    if vc.is_playing():
        vc.stop()
        await asyncio.sleep(0.2)
    vc.play(src)
    while vc.is_playing():
        await asyncio.sleep(0.25)


# === Autocomplete ===
async def audible_autocomplete(interaction: discord.Interaction, current: str):
    current_lower = current.lower()
    names = [n for n in AUDIBLES if current_lower in n.lower()]
    names.sort()
    return [app_commands.Choice(name=n, value=n) for n in names[:25]]


# === Events ===
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Sync failed: {e}")


# === Command ===
@bot.tree.command(name="audible", description="Post visual & autoplay audio", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(name="Start typing to search audibles")
@app_commands.autocomplete(name=audible_autocomplete)
async def audible(interaction: discord.Interaction, name: str):
    safe_name = urllib.parse.quote(name)
    mp4_url = f"{BASE_URL}/{safe_name}.mp4"
    mp3_url = f"{BASE_URL}/{safe_name}.mp3"

    await interaction.response.defer()

    # Send MP4 (autoplays muted)
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(mp4_url) as resp:
                if resp.status == 200:
                    buf = io.BytesIO(await resp.read())
                    await interaction.followup.send(file=discord.File(buf, filename=f"{name}.mp4"))
                else:
                    await interaction.followup.send(f"⚠️ No video for {name} (HTTP {resp.status})")
    except Exception as e:
        await interaction.followup.send(f"❌ Video fetch error: {e}")

    # Play MP3 in VC
    if not (interaction.user.voice and interaction.user.voice.channel):
        await interaction.followup.send("🚫 You must be in a voice channel.")
        return

    lock = guild_lock(interaction.guild.id)
    async with lock:
        try:
            vc = await connect_vc(interaction.user.voice.channel)
        except Exception as e:
            await interaction.followup.send(f"❌ Can’t connect to voice: {e}")
            return

        try:
            await play_mp3(vc, mp3_url)
        except Exception as e:
            await interaction.followup.send(f"❌ Playback error: {e}")
        finally:
            await asyncio.sleep(0.3)
            with contextlib.suppress(Exception):
                await vc.disconnect(force=True)


bot.run(TOKEN)
