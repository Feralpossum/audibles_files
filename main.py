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
            discord.SelectOption(label=name, description=data["description"])
            for name, data in AUDIBLES.items()
        ]
        super().__init__(placeholder="Choose your audible!", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        mp4_url = AUDIBLES[choice]["url"]
        mp3_url = mp4_url.replace(".mp4", ".mp3")

        await interaction.response.defer()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(mp4_url, headers=USER_AGENT_HEADER) as resp:
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
            await interaction.followup.send(f"❌ Voice playback error: ```{e}```")

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

asyncio.run(main())
