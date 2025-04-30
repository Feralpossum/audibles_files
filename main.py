import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import io
import os
import subprocess
from aiohttp import web

# --- Keep alive server ---
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

# --- Updated Base URL (your raw Vercel link) ---
BASE_URL = "https://audiblesfiles-qsvgvhyeq-karls-projects-20dd944d.vercel.app/Audibles"

# --- Audibles dictionary ---
AUDIBLES = {
    "Boo": {"file": "Boo", "description": "Classic jump scare", "emoji": "🎃"},
    "DoneLosing": {"file": "DoneLosing", "description": "Over it already", "emoji": "🏁"},
    "DontSlipMoppingFloor": {"file": "DontSlipMoppingFloor", "description": "Careful... it's wet!", "emoji": "🧹"},
    "FatGuysNoMoney": {"file": "FatGuysNoMoney", "description": "Hard relatable moment", "emoji": "💸"},
    "FromADrunkenMonkey": {"file": "FromADrunkenMonkey", "description": "Monkey mayhem", "emoji": "🐒"},
    "GreatestEVER": {"file": "GreatestEVER", "description": "All-time hype", "emoji": "🏆"},
    "INeverWinYouSuck": {"file": "INeverWinYouSuck", "description": "Ultimate sore loser", "emoji": "😡"},
    "KeepPunching": {"file": "KeepPunching", "description": "Fight back!", "emoji": "🥊"},
    "LovesomeLovesomeNot": {"file": "LovesomeLovesomeNot", "description": "Love's a battlefield", "emoji": "💔"},
    "Mmm_roar": {"file": "Mmm_roar", "description": "Rawr means love", "emoji": "🦁"},
    "Mwahahaha": {"file": "Mwahahaha", "description": "Evil laugh", "emoji": "😈"},
    "NotEvenSameZipCodeFunny": {"file": "NotEvenSameZipCodeFunny", "description": "You're not even close!", "emoji": "🏡"},
    "Pleasestandstill": {"file": "Pleasestandstill", "description": "Deer in headlights", "emoji": "🦌"},
    "ReallyLonelyBeingYou": {"file": "ReallyLonelyBeingYou", "description": "A tragic roast", "emoji": "😢"},
    "Sandwich": {"file": "Sandwich", "description": "Time for lunch", "emoji": "🥪"},
    "Score": {"file": "Score", "description": "Winning!", "emoji": "🏅"},
    "SeriouslyEvenTrying": {"file": "SeriouslyEvenTrying", "description": "Are you even trying?", "emoji": "🤨"},
    "ShakeLikeItDidntHurt": {"file": "ShakeLikeItDidntHurt", "description": "Shake it off", "emoji": "🕺"},
    "WelcomeExpectingYou": {"file": "WelcomeExpectingYou", "description": "Grand entrance", "emoji": "🎉"},
    "Yawn": {"file": "Yawn", "description": "So bored", "emoji": "🥱"},
}

# --- Dropdown Menu ---
class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=name, description=data["description"], emoji=data["emoji"]) for name, data in AUDIBLES.items()]
        super().__init__(placeholder="Choose your audible!", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        file = AUDIBLES[choice]["file"]
        mp4_url = f"{BASE_URL}/{file}.mp4"
        mp3_url = f"{BASE_URL}/{file}.mp3"

        await interaction.response.defer()

        # --- Send MP4 visual ---
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(mp4_url) as resp:
                    if resp.status == 200:
                        mp4_data = io.BytesIO(await resp.read())
                        await interaction.followup.send(file=discord.File(mp4_data, filename=f"{file}.mp4"))
                    else:
                        await interaction.followup.send(f"Failed to load MP4 for {choice}.")
        except Exception as e:
            await interaction.followup.send(f"Visual playback error: {e}")

        # --- Voice playback if user in voice ---
        if interaction.user.voice and interaction.user.voice.channel:
            try:
                vc = await interaction.user.voice.channel.connect()
                async with aiohttp.ClientSession() as session:
                    async with session.get(mp3_url) as resp:
                        if resp.status != 200:
                            await interaction.followup.send(f"MP3 not found for {choice}")
                            return
                        audio_data = io.BytesIO(await resp.read())

                # --- FFmpeg process ---
                process = subprocess.Popen(
                    ["./ffmpeg", "-i", "pipe:0", "-f", "s16le", "-ar", "48000", "-ac", "2", "pipe:1"],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE
                )
                process.stdin.write(audio_data.getbuffer())
                process.stdin.close()

                audio = discord.PCMAudio(process.stdout)
                vc.play(audio)

                while vc.is_playing():
                    await asyncio.sleep(1)

                await vc.disconnect()
            except Exception as e:
                await interaction.followup.send(f"Voice playback error: {e}")

class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())

# --- Events ---
@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Slash commands synced.")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    bot.add_view(DropdownView())

@bot.tree.command(name="audible", description="Send an audible from the list")
async def audible(interaction: discord.Interaction):
    await interaction.response.send_message("Choose your audible below:", view=DropdownView())

# --- Main Launch ---
async def main():
    asyncio.create_task(run_keep_alive())
    await bot.start(os.environ["DISCORD_TOKEN"])

asyncio.run(main())
