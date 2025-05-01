import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import io
import os
import subprocess
import shutil
import traceback
from aiohttp import web

# --- Keep-alive webserver for Railway ---
async def home(request):
    return web.Response(text="Bot is alive!")

async def run_keep_alive():
    app = web.Application()
    app.router.add_get("/", home)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    await site.start()

# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="/", intents=intents)

# --- User-Agent Header ---
USER_AGENT_HEADER = {"User-Agent": "Mozilla/5.0"}

# --- Audibles ---
# --- 20 Audibles with Explicit URLs ---
AUDIBLES = {
    "Boo": {"url": "https://audiblesfiles.vercel.app/Audibles/Boo.mp4", "description": "Classic jump scare"},
    "DoneLosing": {"url": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp4", "description": "Over it already"},
    "DontSlipMoppingFloor": {"url": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp4", "description": "Careful... it's wet!"},
    "FatGuysNoMoney": {"url": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp4", "description": "Hard relatable moment"},
    "FromADrunkenMonkey": {"url": "https://audiblesfiles.vercel.app/Audibles/FromADrunkenMonkey.mp4", "description": "Monkey mayhem"},
    "GreatestEVER": {"url": "https://audiblesfiles.vercel.app/Audibles/GreatestEVER.mp4", "description": "All-time hype"},
    "INeverWinYouSuck": {"url": "https://audiblesfiles.vercel.app/Audibles/INeverWinYouSuck.mp4", "description": "Ultimate sore loser"},
    "KeepPunching": {"url": "https://audiblesfiles.vercel.app/Audibles/KeepPunching.mp4", "description": "Fight back!"},
    "LovesomeLovesomeNot": {"url": "https://audiblesfiles.vercel.app/Audibles/LovesomeLovesomeNot.mp4", "description": "Love's a battlefield"},
    "Mmm_roar": {"url": "https://audiblesfiles.vercel.app/Audibles/Mmm_roar.mp4", "description": "Rawr means love"},
    "Mwahahaha": {"url": "https://audiblesfiles.vercel.app/Audibles/Mwahahaha.mp4", "description": "Evil laugh"},
    "NotEvenSameZipCodeFunny": {"url": "https://audiblesfiles.vercel.app/Audibles/NotEvenSameZipCodeFunny.mp4", "description": "You're not even close!"},
    "Pleasestandstill": {"url": "https://audiblesfiles.vercel.app/Audibles/Pleasestandstill.mp4", "description": "Deer in headlights"},
    "ReallyLonelyBeingYou": {"url": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp4", "description": "A tragic roast"},
    "Sandwich": {"url": "https://audiblesfiles.vercel.app/Audibles/Sandwich.mp4", "description": "Time for lunch"},
    "Score": {"url": "https://audiblesfiles.vercel.app/Audibles/Score.mp4", "description": "Winning!"},
    "SeriouslyEvenTrying": {"url": "https://audiblesfiles.vercel.app/Audibles/SeriouslyEvenTrying.mp4", "description": "Are you even trying?"},
    "ShakeLikeItDidntHurt": {"url": "https://audiblesfiles.vercel.app/Audibles/ShakeLikeItDidntHurt.mp4", "description": "Shake it off"},
    "WelcomeExpectingYou": {"url": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp4", "description": "Grand entrance"},
    "Yawn": {"url": "https://audiblesfiles.vercel.app/Audibles/Yawn.mp4", "description": "So bored"}
    "Boo": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/Boo.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Boo.mp3", "description": "Classic jump scare"},
    "DoneLosing": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp3", "description": "Over it already"},
    "DontSlipMoppingFloor": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp3", "description": "Careful... it's wet!"},
    "FatGuysNoMoney": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp3", "description": "Hard relatable moment"},
    "FromADrunkenMonkey": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/FromADrunkenMonkey.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/FromADrunkenMonkey.mp3", "description": "Monkey mayhem"},
    "GreatestEVER": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/GreatestEVER.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/GreatestEVER.mp3", "description": "All-time hype"},
    "INeverWinYouSuck": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/INeverWinYouSuck.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/INeverWinYouSuck.mp3", "description": "Ultimate sore loser"},
    "KeepPunching": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/KeepPunching.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/KeepPunching.mp3", "description": "Fight back!"},
    "LovesomeLovesomeNot": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/LovesomeLovesomeNot.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/LovesomeLovesomeNot.mp3", "description": "Love's a battlefield"},
    "Mmm_roar": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/Mmm_roar.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Mmm_roar.mp3", "description": "Rawr means love"},
    "Mwahahaha": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/Mwahahaha.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Mwahahaha.mp3", "description": "Evil laugh"},
    "NotEvenSameZipCodeFunny": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/NotEvenSameZipCodeFunny.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/NotEvenSameZipCodeFunny.mp3", "description": "You're not even close!"},
    "Pleasestandstill": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/Pleasestandstill.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Pleasestandstill.mp3", "description": "Deer in headlights"},
    "ReallyLonelyBeingYou": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp3", "description": "A tragic roast"},
    "Sandwich": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/Sandwich.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Sandwich.mp3", "description": "Time for lunch"},
    "Score": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/Score.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Score.mp3", "description": "Winning!"},
    "SeriouslyEvenTrying": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/SeriouslyEvenTrying.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/SeriouslyEvenTrying.mp3", "description": "Are you even trying?"},
    "ShakeLikeItDidntHurt": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/ShakeLikeItDidntHurt.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/ShakeLikeItDidntHurt.mp3", "description": "Shake it off"},
    "WelcomeExpectingYou": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp3", "description": "Grand entrance"},
    "Yawn": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/Yawn.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Yawn.mp3", "description": "So bored"},
}

# --- Determine ffmpeg executable path ---
def get_ffmpeg_executable():
    if os.path.isfile("./ffmpeg") and os.access("./ffmpeg", os.X_OK):
        return "./ffmpeg"
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    raise FileNotFoundError("ffmpeg not found")

# --- Dropdown ---
# --- Dropdown UI ---
class Dropdown(discord.ui.Select):
def __init__(self):
options = [
@@ -75,45 +47,37 @@ def __init__(self):

async def callback(self, interaction: discord.Interaction):
choice = self.values[0]
        mp4_url = AUDIBLES[choice]["url"]
        mp3_url = mp4_url.replace(".mp4", ".mp3")
        mp4_url = AUDIBLES[choice]["mp4_url"]
        mp3_url = AUDIBLES[choice]["mp3_url"]

await interaction.response.defer()

try:
async with aiohttp.ClientSession() as session:
                async with session.get(mp4_url, headers=USER_AGENT_HEADER) as resp:
                async with session.get(mp4_url) as resp:
if resp.status == 200:
mp4_data = io.BytesIO(await resp.read())
await interaction.followup.send(file=discord.File(mp4_data, filename=f"{choice}.mp4"))
else:
                        async with session.get(mp4_url) as retry_resp:
                            if retry_resp.status == 200:
                                mp4_data = io.BytesIO(await retry_resp.read())
                                await interaction.followup.send(file=discord.File(mp4_data, filename=f"{choice}.mp4"))
                            else:
                                await interaction.followup.send(f"⚠️ Couldn't fetch MP4 for `{choice}` (HTTP {retry_resp.status})")

            if interaction.user.voice and interaction.user.voice.channel:
                        await interaction.followup.send(f"⚠️ Couldn't fetch MP4 for `{choice}` (HTTP {resp.status})")
        except Exception as e:
            await interaction.followup.send(f"❌ MP4 error: {e}")

        if interaction.user.voice and interaction.user.voice.channel:
            try:
vc = interaction.guild.voice_client
if not vc:
vc = await interaction.user.voice.channel.connect()

async with aiohttp.ClientSession() as session:
                    async with session.get(mp3_url, headers=USER_AGENT_HEADER) as resp:
                        if resp.status == 200:
                            mp3_data = await resp.read()
                        else:
                            async with session.get(mp3_url) as retry_resp:
                                if retry_resp.status == 200:
                                    mp3_data = await retry_resp.read()
                                else:
                                    await interaction.followup.send(f"⚠️ Couldn't fetch MP3 (HTTP {retry_resp.status})")
                                    return

                ffmpeg_exe = get_ffmpeg_executable()
                    async with session.get(mp3_url) as resp:
                        if resp.status != 200:
                            await interaction.followup.send(f"⚠️ Couldn't fetch MP3 (HTTP {resp.status})")
                            return
                        mp3_data = await resp.read()

process = subprocess.Popen(
                    [ffmpeg_exe, "-i", "pipe:0", "-f", "s16le", "-ar", "48000", "-ac", "2", "pipe:1"],
                    ["./ffmpeg", "-i", "pipe:0", "-f", "s16le", "-ar", "48000", "-ac", "2", "pipe:1"],
stdin=subprocess.PIPE,
stdout=subprocess.PIPE
)
@@ -127,16 +91,33 @@ async def callback(self, interaction: discord.Interaction):
await asyncio.sleep(1)
await vc.disconnect()

        except Exception as e:
            error_details = traceback.format_exc()
            print(error_details)
            await interaction.followup.send(f"❌ Voice playback error: ```{e}```")
            except Exception as e:
                await interaction.followup.send(f"❌ Voice playback error:\n```{e}```")

class DropdownView(discord.ui.View):
def __init__(self):
super().__init__(timeout=None)
self.add_item(Dropdown())

@bot.tree.command(name="audible", description="Send and play an audible")
async def audible(interaction: discord.Interaction):
    await interaction.response.send_message("Choose your audible:", view=DropdownView())

@bot.tree.command(name="ffmpeg_diagnose", description="Test if ffmpeg is working")
async def ffmpeg_diagnose(interaction: discord.Interaction):
    try:
        exists = os.path.isfile("./ffmpeg")
        executable = os.access("./ffmpeg", os.X_OK)
        output = subprocess.check_output(["./ffmpeg", "-version"]).decode("utf-8").splitlines()[0] if exists and executable else "N/A"

        await interaction.response.send_message(
            f"✔️ ./ffmpeg exists: `{exists}`\n"
            f"✔️ Executable: `{executable}`\n"
            f"🔍 Version: `{output}`"
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ ffmpeg diagnose error:\n```{e}```")

@bot.event
async def on_ready():
print(f"✅ Bot is ready: {bot.user}")
@@ -147,47 +128,8 @@ async def on_ready():
print(f"❌ Sync error: {e}")
bot.add_view(DropdownView())

@bot.tree.command(name="audible", description="Send and play an audible")
async def audible(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        await interaction.followup.send("Choose your audible:", view=DropdownView())
    except Exception as e:
        print(f"❌ Error in /audible command: {e}")
        await interaction.followup.send(f"❌ Error: {e}")

@bot.tree.command(name="ffmpeg_diagnose", description="Test if ffmpeg is working")
async def ffmpeg_diagnose(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        messages = []
        if os.path.isfile("./ffmpeg"):
            messages.append("✔️ ./ffmpeg exists")
        else:
            messages.append("❌ ./ffmpeg does NOT exist")

        if os.access("./ffmpeg", os.X_OK):
            messages.append("✔️ ./ffmpeg is executable")
        else:
            messages.append("❌ ./ffmpeg is NOT executable")

        system_ffmpeg = shutil.which("ffmpeg")
        if system_ffmpeg:
            messages.append(f"✔️ System ffmpeg found at: {system_ffmpeg}")
        else:
            messages.append("❌ No system ffmpeg found")

        await interaction.followup.send("\n".join(messages))

    except Exception as e:
        await interaction.followup.send(f"❌ ffmpeg test failed: {e}")

# --- Run Bot ---
async def main():
    try:
        asyncio.create_task(run_keep_alive())
        await bot.start(os.environ["DISCORD_TOKEN"])
    except Exception as e:
        print("❌ Top-level error:", e)
    await bot.start(os.environ["DISCORD_TOKEN"])

asyncio.run(main())
