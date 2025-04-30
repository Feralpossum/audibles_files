import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import io
import os
import subprocess
from aiohttp import web

# --- Keep alive aiohttp webserver ---
async def home(request):
    return web.Response(text="Bot is alive!")

async def run_keep_alive():
    app = web.Application()
    app.router.add_get("/", home)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    await site.start()

# --- Bot setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="/", intents=intents)

# --- 20 Audibles ---
AUDIBLES = {
    "Boo": {"url": "https://audiblesfiles.vercel.app/Audibles/Boo.mp4", "description": "Classic jump scare", "emoji": "🎃"},
    "DoneLosing": {"url": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp4", "description": "Over it already", "emoji": "🏁"},
    "DontSlipMoppingFloor": {"url": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp4", "description": "Careful... it's wet!", "emoji": "🧹"},
    "FatGuysNoMoney": {"url": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp4", "description": "Hard relatable moment", "emoji": "💸"},
    "FromADrunkenMonkey": {"url": "https://audiblesfiles.vercel.app/Audibles/FromADrunkenMonkey.mp4", "description": "Monkey mayhem", "emoji": "🐒"},
    "GreatestEVER": {"url": "https://audiblesfiles.vercel.app/Audibles/GreatestEVER.mp4", "description": "All-time hype", "emoji": "🏆"},
    "INeverWinYouSuck": {"url": "https://audiblesfiles.vercel.app/Audibles/INeverWinYouSuck.mp4", "description": "Ultimate sore loser", "emoji": "😡"},
    "KeepPunching": {"url": "https://audiblesfiles.vercel.app/Audibles/KeepPunching.mp4", "description": "Fight back!", "emoji": "🥊"},
    "LovesomeLovesomeNot": {"url": "https://audiblesfiles.vercel.app/Audibles/LovesomeLovesomeNot.mp4", "description": "Love's a battlefield", "emoji": "💔"},
    "Mmm_roar": {"url": "https://audiblesfiles.vercel.app/Audibles/Mmm_roar.mp4", "description": "Rawr means love", "emoji": "🦁"},
    "Mwahahaha": {"url": "https://audiblesfiles.vercel.app/Audibles/Mwahahaha.mp4", "description": "Evil laugh", "emoji": "😈"},
    "NotEvenSameZipCodeFunny": {"url": "https://audiblesfiles.vercel.app/Audibles/NotEvenSameZipCodeFunny.mp4", "description": "You're not even close!", "emoji": "🏡"},
    "Pleasestandstill": {"url": "https://audiblesfiles.vercel.app/Audibles/Pleasestandstill.mp4", "description": "Deer in headlights", "emoji": "🦌"},
    "ReallyLonelyBeingYou": {"url": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp4", "description": "A tragic roast", "emoji": "😢"},
    "Sandwich": {"url": "https://audiblesfiles.vercel.app/Audibles/Sandwich.mp4", "description": "Time for lunch", "emoji": "🥪"},
    "Score": {"url": "https://audiblesfiles.vercel.app/Audibles/Score.mp4", "description": "Winning!", "emoji": "🏅"},
    "SeriouslyEvenTrying": {"url": "https://audiblesfiles.vercel.app/Audibles/SeriouslyEvenTrying.mp4", "description": "Are you even trying?", "emoji": "🤨"},
    "ShakeLikeItDidntHurt": {"url": "https://audiblesfiles.vercel.app/Audibles/ShakeLikeItDidntHurt.mp4", "description": "Shake it off", "emoji": "🕺"},
    "WelcomeExpectingYou": {"url": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp4", "description": "Grand entrance", "emoji": "🎉"},
    "Yawn": {"url": "https://audiblesfiles.vercel.app/Audibles/Yawn.mp4", "description": "So bored", "emoji": "🥱"},
}

# --- Dropdown Menu ---
class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=name, description=data["description"], emoji=data.get("emoji")) for name, data in AUDIBLES.items()]
        super().__init__(placeholder="Choose your audible!", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        audible = AUDIBLES[choice]
        mp4_url = audible["url"]

        await interaction.response.defer()

        # --- Fetch MP4 ---
        async with aiohttp.ClientSession() as session:
            async with session.get(mp4_url) as resp:
                if resp.status != 200:
                    await interaction.followup.send(f"Error fetching MP4 for {choice}.")
                    return
                data = io.BytesIO(await resp.read())

        # --- Parallel task: Send MP4 to chat immediately ---
        asyncio.create_task(interaction.followup.send(file=discord.File(data, filename=f"{choice}.mp4")))

        # --- If user in VC, join and play ---
        if interaction.user.voice and interaction.user.voice.channel:
            vc = await interaction.user.voice.channel.connect()

            ffmpeg_cmd = [
                "./ffmpeg", "-i", "pipe:0",
                "-f", "s16le",
                "-ar", "48000",
                "-ac", "2",
                "pipe:1"
            ]
            process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            ffmpeg_input, ffmpeg_output = process.stdin, process.stdout

            ffmpeg_input.write(data.getbuffer())
            ffmpeg_input.close()

            audio = discord.PCMAudio(ffmpeg_output)
            vc.play(audio)

            # Disconnect after playing
            while vc.is_playing():
                await asyncio.sleep(1)
            await vc.disconnect()

class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    bot.add_view(DropdownView())

@bot.tree.command(name="audible", description="Send an audible from the list")
async def audible(interaction: discord.Interaction):
    await interaction.response.send_message("Choose your audible below:", view=DropdownView(), ephemeral=False)

@bot.tree.command(name="ffmpegtest", description="Check if ffmpeg is working")
async def ffmpegtest(interaction: discord.Interaction):
    try:
        result = subprocess.run(["./ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        output = result.stdout or result.stderr
        await interaction.response.send_message(f"```{output[:1900]}```", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"FFmpeg test failed: `{str(e)}`", ephemeral=True)

# --- Launch everything ---
async def main():
    asyncio.create_task(run_keep_alive())
    await bot.start(os.environ["DISCORD_TOKEN"])

asyncio.run(main())
