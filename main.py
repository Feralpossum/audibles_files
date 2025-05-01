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

# --- Vercel Static Base URL ---
BASE_URL = "https://audiblesfiles-qsvgvhyeq-karls-projects-20dd944d.vercel.app/Audibles"

# --- 20 Audibles ---
AUDIBLES = {
    "Boo": {"description": "Classic jump scare", "emoji": "🎃"},
    "DoneLosing": {"description": "Over it already", "emoji": "🏑"},
    "DontSlipMoppingFloor": {"description": "Careful... it's wet!", "emoji": "🭹"},
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
    "Yawn": {"description": "So bored", "emoji": "🤫"},
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
class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, description=data["description"], emoji=data["emoji"])
            for name, data in AUDIBLES.items()
        ]
        super().__init__(placeholder="Choose your audible!", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        mp4_url = f"{BASE_URL}/{choice}.mp4"
        mp3_url = f"{BASE_URL}/{choice}.mp3"

        await interaction.response.defer()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(mp4_url) as resp:
                    if resp.status == 200:
                        mp4_data = io.BytesIO(await resp.read())
                        await interaction.followup.send(file=discord.File(mp4_data, filename=f"{choice}.mp4"))
                    else:
                        await interaction.followup.send(f"⚠️ Couldn't fetch MP4 for `{choice}` (HTTP {resp.status})")

            if interaction.user.voice and interaction.user.voice.channel:
                vc = interaction.guild.voice_client
                if not vc:
                    vc = await interaction.user.voice.channel.connect()

                async with aiohttp.ClientSession() as session:
                    async with session.get(mp3_url) as resp:
                        if resp.status != 200:
                            await interaction.followup.send(f"⚠️ Couldn't fetch MP3 (HTTP {resp.status})")
                            return
                        mp3_data = await resp.read()

                ffmpeg_exe = get_ffmpeg_executable()
                process = subprocess.Popen(
                    [ffmpeg_exe, "-i", "pipe:0", "-f", "s16le", "-ar", "48000", "-ac", "2", "pipe:1"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE
                )
                process.stdin.write(mp3_data)
                process.stdin.close()

                audio = discord.PCMAudio(process.stdout)
                vc.play(audio)

                while vc.is_playing():
                    await asyncio.sleep(1)
                await vc.disconnect()

        except Exception as e:
            error_details = traceback.format_exc()
            print(error_details)
            await interaction.followup.send(f"❌ Voice playback error:\n```
{e}
```")

class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())

@bot.event
async def on_ready():
    print(f"✅ Bot is ready: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
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
        ffmpeg = get_ffmpeg_executable()
        output = subprocess.check_output([ffmpeg, "-version"], stderr=subprocess.STDOUT, text=True)
        await interaction.followup.send(f"```\n{output[:1900]}\n```")
    except Exception as e:
        await interaction.followup.send(f"❌ ffmpeg test failed: {e}")

# --- Run Bot ---
async def main():
    try:
        asyncio.create_task(run_keep_alive())
        await bot.start(os.environ["DISCORD_TOKEN"])
    except Exception as e:
        print("❌ Top-level error:", e)

asyncio.run(main())
