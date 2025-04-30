import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import io
import os
import subprocess
from aiohttp import web

# --- Keep-alive ping webserver ---
async def home(request):
    return web.Response(text="Bot is alive!")

async def run_keep_alive():
    app = web.Application()
    app.router.add_get("/", home)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    await site.start()

# --- Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="/", intents=intents)

# --- Base URL for Vercel assets ---
BASE_URL = "https://audiblesfiles-qsvgvhyeq-karls-projects-20dd944d.vercel.app/Audibles"

# --- All Audibles ---
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
}

# --- Dropdown UI ---
class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=name, description=data["description"], emoji=data["emoji"]) for name, data in AUDIBLES.items()]
        super().__init__(placeholder="Choose your audible!", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        mp4_url = f"{BASE_URL}/{choice}.mp4"
        mp3_url = f"{BASE_URL}/{choice}.mp3"

        await interaction.response.defer()

        # --- Send video in chat ---
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(mp4_url) as resp:
                    if resp.status != 200:
                        await interaction.followup.send(f"Failed to load MP4 for {choice}.")
                        return
                    mp4_data = io.BytesIO(await resp.read())
                    await interaction.followup.send(file=discord.File(mp4_data, filename=f"{choice}.mp4"))
        except Exception as e:
            await interaction.followup.send(f"Error sending video: {e}")

        # --- Play audio in VC ---
        if interaction.user.voice and interaction.user.voice.channel:
            try:
                vc = interaction.guild.voice_client or await interaction.user.voice.channel.connect()

                async with aiohttp.ClientSession() as session:
                    async with session.get(mp3_url) as resp:
                        if resp.status != 200:
                            await interaction.followup.send(f"Failed to load MP3 for {choice}.")
                            return
                        mp3_data = await resp.read()

                ffmpeg = subprocess.Popen(
                    ["./ffmpeg", "-i", "pipe:0", "-f", "s16le", "-ar", "48000", "-ac", "2", "pipe:1"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                )
                ffmpeg.stdin.write(mp3_data)
                ffmpeg.stdin.close()
                audio = discord.PCMAudio(ffmpeg.stdout)

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

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✔️ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Sync failed: {e}")
    bot.add_view(DropdownView())

@bot.tree.command(name="audible", description="Send an audible from the list")
async def audible(interaction: discord.Interaction):
    await interaction.response.send_message("Choose your audible below:", view=DropdownView(), ephemeral=False)

# --- Run Bot ---
async def main():
    asyncio.create_task(run_keep_alive())
    await bot.start(os.environ["DISCORD_TOKEN"])

asyncio.run(main())
