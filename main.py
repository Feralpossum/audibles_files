import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import io
import os
import subprocess
from aiohttp import web

# --- Keep-alive for Railway ---
async def home(request):
    return web.Response(text="Bot is alive!")

async def run_keep_alive():
    app = web.Application()
    app.router.add_get("/", home)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    await site.start()

# --- Discord bot setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="/", intents=intents)

# --- 20 Audibles ---
BASE = "https://audiblesfiles.vercel.app/Audibles"
AUDIBLES = {
    "Boo": {"url": f"{BASE}/Boo.mp4", "mp3_url": f"{BASE}/Boo.mp3", "description": "Classic jump scare", "emoji": "🎃"},
    "DoneLosing": {"url": f"{BASE}/DoneLosing.mp4", "mp3_url": f"{BASE}/DoneLosing.mp3", "description": "Over it already", "emoji": "🏁"},
    "DontSlipMoppingFloor": {"url": f"{BASE}/DontSlipMoppingFloor.mp4", "mp3_url": f"{BASE}/DontSlipMoppingFloor.mp3", "description": "Careful... it's wet!", "emoji": "🧹"},
    "FatGuysNoMoney": {"url": f"{BASE}/FatGuysNoMoney.mp4", "mp3_url": f"{BASE}/FatGuysNoMoney.mp3", "description": "Hard relatable moment", "emoji": "💸"},
    "FromADrunkenMonkey": {"url": f"{BASE}/FromADrunkenMonkey.mp4", "mp3_url": f"{BASE}/FromADrunkenMonkey.mp3", "description": "Monkey mayhem", "emoji": "🐒"},
    "GreatestEVER": {"url": f"{BASE}/GreatestEVER.mp4", "mp3_url": f"{BASE}/GreatestEVER.mp3", "description": "All-time hype", "emoji": "🏆"},
    "INeverWinYouSuck": {"url": f"{BASE}/INeverWinYouSuck.mp4", "mp3_url": f"{BASE}/INeverWinYouSuck.mp3", "description": "Ultimate sore loser", "emoji": "😡"},
    "KeepPunching": {"url": f"{BASE}/KeepPunching.mp4", "mp3_url": f"{BASE}/KeepPunching.mp3", "description": "Fight back!", "emoji": "🥊"},
    "LovesomeLovesomeNot": {"url": f"{BASE}/LovesomeLovesomeNot.mp4", "mp3_url": f"{BASE}/LovesomeLovesomeNot.mp3", "description": "Love's a battlefield", "emoji": "💔"},
    "Mmm_roar": {"url": f"{BASE}/Mmm_roar.mp4", "mp3_url": f"{BASE}/Mmm_roar.mp3", "description": "Rawr means love", "emoji": "🦁"},
    "Mwahahaha": {"url": f"{BASE}/Mwahahaha.mp4", "mp3_url": f"{BASE}/Mwahahaha.mp3", "description": "Evil laugh", "emoji": "😈"},
    "NotEvenSameZipCodeFunny": {"url": f"{BASE}/NotEvenSameZipCodeFunny.mp4", "mp3_url": f"{BASE}/NotEvenSameZipCodeFunny.mp3", "description": "You're not even close!", "emoji": "🏡"},
    "Pleasestandstill": {"url": f"{BASE}/Pleasestandstill.mp4", "mp3_url": f"{BASE}/Pleasestandstill.mp3", "description": "Deer in headlights", "emoji": "🦌"},
    "ReallyLonelyBeingYou": {"url": f"{BASE}/ReallyLonelyBeingYou.mp4", "mp3_url": f"{BASE}/ReallyLonelyBeingYou.mp3", "description": "A tragic roast", "emoji": "😢"},
    "Sandwich": {"url": f"{BASE}/Sandwich.mp4", "mp3_url": f"{BASE}/Sandwich.mp3", "description": "Time for lunch", "emoji": "🥪"},
    "Score": {"url": f"{BASE}/Score.mp4", "mp3_url": f"{BASE}/Score.mp3", "description": "Winning!", "emoji": "🏅"},
    "SeriouslyEvenTrying": {"url": f"{BASE}/SeriouslyEvenTrying.mp4", "mp3_url": f"{BASE}/SeriouslyEvenTrying.mp3", "description": "Are you even trying?", "emoji": "🤨"},
    "ShakeLikeItDidntHurt": {"url": f"{BASE}/ShakeLikeItDidntHurt.mp4", "mp3_url": f"{BASE}/ShakeLikeItDidntHurt.mp3", "description": "Shake it off", "emoji": "🕺"},
    "WelcomeExpectingYou": {"url": f"{BASE}/WelcomeExpectingYou.mp4", "mp3_url": f"{BASE}/WelcomeExpectingYou.mp3", "description": "Grand entrance", "emoji": "🎉"},
    "Yawn": {"url": f"{BASE}/Yawn.mp4", "mp3_url": f"{BASE}/Yawn.mp3", "description": "So bored", "emoji": "🥱"},
}

# --- FFmpeg diagnostic command ---
@bot.tree.command(name="ffmpegcheck", description="Check if ffmpeg is available and working")
async def ffmpegcheck(interaction: discord.Interaction):
    try:
        result = subprocess.run(["./ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
        await interaction.response.send_message(f"```{result.stdout[:1800]}```")
    except Exception as e:
        await interaction.response.send_message(f"FFmpeg error: {e}")

# --- Dropdown menu ---
class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=k, description=v["description"], emoji=v["emoji"]) for k, v in AUDIBLES.items()]
        super().__init__(placeholder="Pick an audible", options=options)

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        audible = AUDIBLES[choice]
        await interaction.response.defer()

        # Send MP4 to chat
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(audible["url"]) as resp:
                    if resp.status != 200:
                        await interaction.followup.send("MP4 fetch failed.")
                        return
                    file_data = io.BytesIO(await resp.read())
                    await interaction.followup.send(file=discord.File(file_data, filename=f"{choice}.mp4"))
        except Exception as e:
            await interaction.followup.send(f"MP4 error: {e}")
            return

        # Try voice playback
        if interaction.user.voice and interaction.user.voice.channel:
            vc = await interaction.user.voice.channel.connect()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(audible["mp3_url"]) as resp:
                        if resp.status != 200:
                            await interaction.followup.send("MP3 fetch failed.")
                            await vc.disconnect()
                            return
                        mp3_data = await resp.read()

                if not mp3_data:
                    await interaction.followup.send("MP3 file was empty.")
                    await vc.disconnect()
                    return

                process = subprocess.Popen(
                    ["./ffmpeg", "-i", "pipe:0", "-f", "s16le", "-ar", "48000", "-ac", "2", "pipe:1"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                pcm_audio, stderr = process.communicate(mp3_data)

                if not pcm_audio or len(pcm_audio) < 1024:
                    await interaction.followup.send(f"FFmpeg output error. Stderr:\n```{stderr.decode()[:1000]}```")
                    await vc.disconnect()
                    return

                audio = discord.PCMAudio(io.BytesIO(pcm_audio))
                vc.play(audio)

                while vc.is_playing():
                    await asyncio.sleep(1)
                await vc.disconnect()
            except Exception as e:
                await interaction.followup.send(f"Voice playback error: {e}")
                if vc.is_connected():
                    await vc.disconnect()

# --- UI Wrapper ---
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())

# --- Ready event ---
@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    try:
        await bot.tree.sync()
        print("✅ Slash commands synced.")
    except Exception as e:
        print(f"❌ Sync error: {e}")
    bot.add_view(DropdownView())

@bot.tree.command(name="audible", description="Send an audible and play it in VC")
async def audible(interaction: discord.Interaction):
    await interaction.response.send_message("🎧 Choose your audible:", view=DropdownView(), ephemeral=False)

# --- Run all ---
async def main():
    asyncio.create_task(run_keep_alive())
    await bot.start(os.environ["DISCORD_TOKEN"])

asyncio.run(main())

