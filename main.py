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

# --- All 20 Audibles with mp4 and mp3 URLs ---
AUDIBLES = {
    "Boo": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Boo.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Boo.mp3",
        "description": "Classic jump scare",
        "emoji": "🎃"
    },
    "DoneLosing": {
        "url": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp3",
        "description": "Over it already",
        "emoji": "🏁"
    },
    "DontSlipMoppingFloor": {
        "url": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp3",
        "description": "Careful... it's wet!",
        "emoji": "🧹"
    },
    "FatGuysNoMoney": {
        "url": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp3",
        "description": "Hard relatable moment",
        "emoji": "💸"
    },
    "FromADrunkenMonkey": {
        "url": "https://audiblesfiles.vercel.app/Audibles/FromADrunkenMonkey.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/FromADrunkenMonkey.mp3",
        "description": "Monkey mayhem",
        "emoji": "🐒"
    },
    "GreatestEVER": {
        "url": "https://audiblesfiles.vercel.app/Audibles/GreatestEVER.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/GreatestEVER.mp3",
        "description": "All-time hype",
        "emoji": "🏆"
    },
    "INeverWinYouSuck": {
        "url": "https://audiblesfiles.vercel.app/Audibles/INeverWinYouSuck.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/INeverWinYouSuck.mp3",
        "description": "Ultimate sore loser",
        "emoji": "😡"
    },
    "KeepPunching": {
        "url": "https://audiblesfiles.vercel.app/Audibles/KeepPunching.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/KeepPunching.mp3",
        "description": "Fight back!",
        "emoji": "🥊"
    },
    "LovesomeLovesomeNot": {
        "url": "https://audiblesfiles.vercel.app/Audibles/LovesomeLovesomeNot.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/LovesomeLovesomeNot.mp3",
        "description": "Love's a battlefield",
        "emoji": "💔"
    },
    "Mmm_roar": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Mmm_roar.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Mmm_roar.mp3",
        "description": "Rawr means love",
        "emoji": "🦁"
    },
    "Mwahahaha": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Mwahahaha.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Mwahahaha.mp3",
        "description": "Evil laugh",
        "emoji": "😈"
    },
    "NotEvenSameZipCodeFunny": {
        "url": "https://audiblesfiles.vercel.app/Audibles/NotEvenSameZipCodeFunny.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/NotEvenSameZipCodeFunny.mp3",
        "description": "You're not even close!",
        "emoji": "🏡"
    },
    "Pleasestandstill": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Pleasestandstill.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Pleasestandstill.mp3",
        "description": "Deer in headlights",
        "emoji": "🦌"
    },
    "ReallyLonelyBeingYou": {
        "url": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp3",
        "description": "A tragic roast",
        "emoji": "😢"
    },
    "Sandwich": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Sandwich.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Sandwich.mp3",
        "description": "Time for lunch",
        "emoji": "🥪"
    },
    "Score": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Score.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Score.mp3",
        "description": "Winning!",
        "emoji": "🏅"
    },
    "SeriouslyEvenTrying": {
        "url": "https://audiblesfiles.vercel.app/Audibles/SeriouslyEvenTrying.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/SeriouslyEvenTrying.mp3",
        "description": "Are you even trying?",
        "emoji": "🤨"
    },
    "ShakeLikeItDidntHurt": {
        "url": "https://audiblesfiles.vercel.app/Audibles/ShakeLikeItDidntHurt.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/ShakeLikeItDidntHurt.mp3",
        "description": "Shake it off",
        "emoji": "🕺"
    },
    "WelcomeExpectingYou": {
        "url": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp3",
        "description": "Grand entrance",
        "emoji": "🎉"
    },
    "Yawn": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Yawn.mp4",
        "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Yawn.mp3",
        "description": "So bored",
        "emoji": "🥱"
    }
}

# --- Dropdown Menu ---
class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=name,
                description=data["description"],
                emoji=data["emoji"]
            ) for name, data in AUDIBLES.items()
        ]
        super().__init__(placeholder="Choose your audible!", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        audible = AUDIBLES[choice]
        await interaction.response.defer()

        # --- Send MP4 visually ---
        async with aiohttp.ClientSession() as session:
            async with session.get(audible["url"]) as resp:
                if resp.status != 200:
                    await interaction.followup.send(f"Error fetching MP4 for {choice}.")
                    return
                data = io.BytesIO(await resp.read())
        asyncio.create_task(interaction.followup.send(file=discord.File(data, filename=f"{choice}.mp4")))

        # --- Play MP3 if in VC ---
        if interaction.user.voice and interaction.user.voice.channel:
            try:
                vc = await interaction.user.voice.channel.connect()

                ffmpeg_cmd = [
                    "./ffmpeg", "-re",
                    "-i", audible["mp3_url"],
                    "-f", "s16le",
                    "-ar", "48000",
                    "-ac", "2",
                    "pipe:1"
                ]
                process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE)
                audio = discord.PCMAudio(process.stdout)
                vc.play(audio)

                while vc.is_playing():
                    await asyncio.sleep(1)
                await vc.disconnect()
            except Exception as e:
                await interaction.followup.send(f"Voice playback error: {e}")
                if interaction.guild.voice_client:
                    await interaction.guild.voice_client.disconnect()

class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())

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
    await interaction.response.send_message("Choose your audible below:", view=DropdownView(), ephemeral=False)

# --- Launch bot ---
async def main():
    asyncio.create_task(run_keep_alive())
    await bot.start(os.environ["DISCORD_TOKEN"])

asyncio.run(main())
