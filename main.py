import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import io
import os
from aiohttp import web

# --- Keep alive webserver ---
async def home(request):
    return web.Response(text="Bot is running!")

def keep_alive():
    app = web.Application()
    app.router.add_get("/", home)
    runner = web.AppRunner(app)

    async def run():
        await runner.setup()
        site = web.TCPSite(runner, port=int(os.environ.get("PORT", 8080)))
        await site.start()

    bot.loop.create_task(run())

# --- Bot setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="/", intents=intents)

# --- Your 20 audibles ---
AUDIBLES = {
    "Boo": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Boo.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/Boo.mp3",
        "description": "Classic jump scare",
        "emoji": "🎃"
    },
    "DoneLosing": {
        "url": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp3",
        "description": "Over it already",
        "emoji": "🏁"
    },
    "DontSlipMoppingFloor": {
        "url": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp3",
        "description": "Careful... it's wet!",
        "emoji": "🧹"
    },
    "FatGuysNoMoney": {
        "url": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp3",
        "description": "Hard relatable moment",
        "emoji": "💸"
    },
    "FromADrunkenMonkey": {
        "url": "https://audiblesfiles.vercel.app/Audibles/FromADrunkenMonkey.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/FromADrunkenMonkey.mp3",
        "description": "Monkey mayhem",
        "emoji": "🐒"
    },
    "GreatestEVER": {
        "url": "https://audiblesfiles.vercel.app/Audibles/GreatestEVER.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/GreatestEVER.mp3",
        "description": "All-time hype",
        "emoji": "🏆"
    },
    "INeverWinYouSuck": {
        "url": "https://audiblesfiles.vercel.app/Audibles/INeverWinYouSuck.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/INeverWinYouSuck.mp3",
        "description": "Ultimate sore loser",
        "emoji": "😡"
    },
    "KeepPunching": {
        "url": "https://audiblesfiles.vercel.app/Audibles/KeepPunching.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/KeepPunching.mp3",
        "description": "Fight back!",
        "emoji": "🥊"
    },
    "LovesomeLovesomeNot": {
        "url": "https://audiblesfiles.vercel.app/Audibles/LovesomeLovesomeNot.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/LovesomeLovesomeNot.mp3",
        "description": "Love's a battlefield",
        "emoji": "💔"
    },
    "Mmm_roar": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Mmm_roar.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/Mmm_roar.mp3",
        "description": "Rawr means love",
        "emoji": "🦁"
    },
    "Mwahahaha": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Mwahahaha.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/Mwahahaha.mp3",
        "description": "Evil laugh",
        "emoji": "😈"
    },
    "NotEvenSameZipCodeFunny": {
        "url": "https://audiblesfiles.vercel.app/Audibles/NotEvenSameZipCodeFunny.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/NotEvenSameZipCodeFunny.mp3",
        "description": "You're not even close!",
        "emoji": "🏡"
    },
    "Pleasestandstill": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Pleasestandstill.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/Pleasestandstill.mp3",
        "description": "Deer in headlights",
        "emoji": "🦌"
    },
    "ReallyLonelyBeingYou": {
        "url": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp3",
        "description": "A tragic roast",
        "emoji": "😢"
    },
    "Sandwich": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Sandwich.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/Sandwich.mp3",
        "description": "Time for lunch",
        "emoji": "🥪"
    },
    "Score": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Score.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/Score.mp3",
        "description": "Winning!",
        "emoji": "🏅"
    },
    "SeriouslyEvenTrying": {
        "url": "https://audiblesfiles.vercel.app/Audibles/SeriouslyEvenTrying.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/SeriouslyEvenTrying.mp3",
        "description": "Are you even trying?",
        "emoji": "🤨"
    },
    "ShakeLikeItDidntHurt": {
        "url": "https://audiblesfiles.vercel.app/Audibles/ShakeLikeItDidntHurt.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/ShakeLikeItDidntHurt.mp3",
        "description": "Shake it off",
        "emoji": "🕺"
    },
    "WelcomeExpectingYou": {
        "url": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp3",
        "description": "Grand entrance",
        "emoji": "🎉"
    },
    "Yawn": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Yawn.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/Yawn.mp3",
        "description": "So bored",
        "emoji": "🥱"
    }
}

# (Dropdown and callback coming next — it’s too long for one message)
# --- Dropdown selection class ---
class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=name,
                description=data["description"],
                emoji=data.get("emoji")
            )
            for name, data in AUDIBLES.items()
        ]
        super().__init__(
            placeholder="Choose your audible!",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="audible_dropdown"
        )

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        audible = AUDIBLES[choice]
        mp4_url = audible["url"]
        mp3_url = audible.get("audio")

        await interaction.response.defer()

        # Try to join voice channel and play sound
        if interaction.user.voice and mp3_url:
            try:
                vc = await interaction.user.voice.channel.connect()
                async with aiohttp.ClientSession() as session:
                    async with session.get(mp3_url) as resp:
                        if resp.status != 200:
                            await interaction.followup.send('Could not download audio file.', ephemeral=True)
                            return
                        data = io.BytesIO(await resp.read())

                audio_source = discord.FFmpegPCMAudio(data, pipe=True)
                vc.play(audio_source)

                # Wait for audio to finish
                while vc.is_playing():
                    await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=1))
                await vc.disconnect()

            except Exception as e:
                print(f"Voice playback error: {e}")
                if vc.is_connected():
                    await vc.disconnect()

        # Always send MP4 in text chat
        async with aiohttp.ClientSession() as session:
            async with session.get(mp4_url) as resp:
                if resp.status != 200:
                    await interaction.followup.send('Could not download video file.', ephemeral=True)
                    return
                data = io.BytesIO(await resp.read())

        file = discord.File(data, filename=f"{choice}.mp4")
        await interaction.followup.send(file=file)

# --- Dropdown view class ---
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())

# --- Bot events ---
@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    bot.add_view(DropdownView())

# --- Slash command ---
@bot.tree.command(name="audible", description="Send an audible from the list")
async def audible(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Choose your audible below:",
        view=DropdownView(),
        ephemeral=False
    )

# --- Keep-alive and run bot ---
keep_alive()
bot.run(os.environ["DISCORD_TOKEN"])



