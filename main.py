import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import io
import os

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Your 20 audible MP4s hosted on Vercel
AUDIBLES = {
    "Boo": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Boo.mp4",
        "description": "Classic jump scare",
        "emoji": "🎃"
    },
    "DoneLosing": {
        "url": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp4",
        "description": "Over it already",
        "emoji": "🏁"
    },
    "DontSlipMoppingFloor": {
        "url": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp4",
        "description": "Careful... it's wet!",
        "emoji": "🧹"
    },
    "FatGuysNoMoney": {
        "url": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp4",
        "description": "Hard relatable moment",
        "emoji": "💸"
    },
    "FromADrunkenMonkey": {
        "url": "https://audiblesfiles.vercel.app/Audibles/FromADrunkenMonkey.mp4",
        "description": "Monkey mayhem",
        "emoji": "🐒"
    },
    "GreatestEVER": {
        "url": "https://audiblesfiles.vercel.app/Audibles/GreatestEVER.mp4",
        "description": "All-time hype",
        "emoji": "🏆"
    },
    "INeverWinYouSuck": {
        "url": "https://audiblesfiles.vercel.app/Audibles/INeverWinYouSuck.mp4",
        "description": "Ultimate sore loser",
        "emoji": "😡"
    },
    "KeepPunching": {
        "url": "https://audiblesfiles.vercel.app/Audibles/KeepPunching.mp4",
        "description": "Fight back!",
        "emoji": "🥊"
    },
    "LovesomeLovesomeNot": {
        "url": "https://audiblesfiles.vercel.app/Audibles/LovesomeLovesomeNot.mp4",
        "description": "Love's a battlefield",
        "emoji": "💔"
    },
    "Mmm_roar": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Mmm_roar.mp4",
        "description": "Rawr means love",
        "emoji": "🦁"
    },
    "Mwahahaha": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Mwahahaha.mp4",
        "description": "Evil laugh",
        "emoji": "😈"
    },
    "NotEvenSameZipCodeFunny": {
        "url": "https://audiblesfiles.vercel.app/Audibles/NotEvenSameZipCodeFunny.mp4",
        "description": "You're not even close!",
        "emoji": "🏡"
    },
    "Pleasestandstill": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Pleasestandstill.mp4",
        "description": "Deer in headlights",
        "emoji": "🦌"
    },
    "ReallyLonelyBeingYou": {
        "url": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp4",
        "description": "A tragic roast",
        "emoji": "😢"
    },
    "Sandwich": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Sandwich.mp4",
        "description": "Time for lunch",
        "emoji": "🥪"
    },
    "Score": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Score.mp4",
        "description": "Winning!",
        "emoji": "🏅"
    },
    "SeriouslyEvenTrying": {
        "url": "https://audiblesfiles.vercel.app/Audibles/SeriouslyEvenTrying.mp4",
        "description": "Are you even trying?",
        "emoji": "🤨"
    },
    "ShakeLikeItDidntHurt": {
        "url": "https://audiblesfiles.vercel.app/Audibles/ShakeLikeItDidntHurt.mp4",
        "description": "Shake it off",
        "emoji": "🕺"
    },
    "WelcomeExpectingYou": {
        "url": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp4",
        "description": "Grand entrance",
        "emoji": "🎉"
    },
    "Yawn": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Yawn.mp4",
        "description": "So bored",
        "emoji": "🥱"
    }
}

# Dropdown selection class
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
        url = AUDIBLES[choice]["url"]

        await interaction.response.defer()  # ✅ Acknowledge immediately to avoid timeout

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await interaction.followup.send('Could not download file.', ephemeral=True)
                    return
                data = io.BytesIO(await resp.read())

        file = discord.File(data, filename=f"{choice}.mp4")

        await interaction.followup.send(file=file)  # ✅ Final file upload (autoplay)

# Dropdown view class
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())

# Bot startup event
@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    bot.add_view(DropdownView())

# Slash command
@bot.tree.command(name="audible", description="Send an audible from the list")
async def audible(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Choose your audible below:",
        view=DropdownView(),
        ephemeral=False
    )

# Run bot
bot.run(os.environ["DISCORD_TOKEN"])
