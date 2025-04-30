import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import io
import os
from aiohttp import web

# --- Keep Alive for Railway ---
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

# --- Audibles (20 total) ---
BASE_URL = "https://audiblesfiles.vercel.app/Audibles"
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

        # Step 1: Post MP4 to chat
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(mp4_url) as resp:
                    if resp.status == 200:
                        file_bytes = io.BytesIO(await resp.read())
                        await interaction.followup.send(file=discord.File(file_bytes, filename=f"{choice}.mp4"))
                    else:
                        await interaction.followup.send(f"❌ Couldn't load MP4 for `{choice}`.")
        except Exception as e:
            await interaction.followup.send(f"❌ MP4 error: {e}")
            return

        # Step 2: Play MP3 if user is in voice
        if interaction.user.voice and interaction.user.voice.channel:
            try:
                vc = await interaction.user.voice.channel.connect()
                audio = discord.FFmpegPCMAudio(mp3_url, executable="./ffmpeg")
                vc.play(audio)

                while vc.is_playing():
                    await asyncio.sleep(1)

                await vc.disconnect()
            except Exception as e:
                await interaction.followup.send(f"🔇 Voice playback error: {e}")

# --- View Container ---
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())

# --- Ready Event ---
@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    try:
        await bot.tree.sync()
        print("✅ Slash commands synced.")
    except Exception as e:
        print(f"❌ Sync error: {e}")
    bot.add_view(DropdownView())

# --- Slash Command ---
@bot.tree.command(name="audible", description="Send an audible with voice + video")
async def audible(interaction: discord.Interaction):
    await interaction.response.send_message("🎧 Choose an audible:", view=DropdownView(), ephemeral=False)

# --- Main Entry ---
async def main():
    asyncio.create_task(run_keep_alive())
    await bot.start(os.environ["DISCORD_TOKEN"])

asyncio.run(main())
