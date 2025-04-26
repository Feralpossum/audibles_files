import discord
from discord.ext import commands
from discord import app_commands
import os

# Bot setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Your audible MP4s hosted on Vercel
AUDIBLES = {
    "Boo": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Boo.mp4",
        "description": "Classic jump scare",
        "emoji": "🎃"
    },
    "ReallyLonelyBeingYou": {
        "url": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp4",
        "description": "A tragic roast",
        "emoji": "😢"
    },
    "WelcomeExpectingYou": {
        "url": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp4",
        "description": "Warm fuzzy welcome",
        "emoji": "👋"
    },
    "HappyBirthday": {
        "url": "https://audiblesfiles.vercel.app/Audibles/HappyBirthday.mp4",
        "description": "Birthday celebration",
        "emoji": "🎂"
    },
    "EpicFail": {
        "url": "https://audiblesfiles.vercel.app/Audibles/EpicFail.mp4",
        "description": "Epic fail sound",
        "emoji": "💥"
    },
    "MissionComplete": {
        "url": "https://audiblesfiles.vercel.app/Audibles/MissionComplete.mp4",
        "description": "Victory noise",
        "emoji": "🏆"
    },
    "Surprise": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Surprise.mp4",
        "description": "Shocking surprise",
        "emoji": "🎉"
    },
    "SarcasticClap": {
        "url": "https://audiblesfiles.vercel.app/Audibles/SarcasticClap.mp4",
        "description": "Mock applause",
        "emoji": "👏"
    },
    "Oops": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Oops.mp4",
        "description": "Oops sound",
        "emoji": "😬"
    },
    "GameOver": {
        "url": "https://audiblesfiles.vercel.app/Audibles/GameOver.mp4",
        "description": "Game over tone",
        "emoji": "🎮"
    },
}

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.tree.command(name="audible", description="Send an audible from the list")
async def audible(interaction: discord.Interaction):
    options = [
        discord.SelectOption(
            label=name,
            description=data["description"],
            emoji=data.get("emoji", None)
        )
        for name, data in AUDIBLES.items()
    ]

    select = discord.ui.Select(
        placeholder="Choose your audible!",
        min_values=1,
        max_values=1,
        options=options
    )

    async def select_callback(interaction2: discord.Interaction):
        choice = select.values[0]
        selected = AUDIBLES[choice]
        embed = discord.Embed(
            title=f"🔊 {choice}",
            description=selected["description"],
            color=discord.Color.blue()
        )
        embed.set_video(url=selected["url"])  # Embeds the MP4 video inside the Discord chat
        await interaction2.response.send_message(embed=embed)

    select.callback = select_callback

    view = discord.ui.View()
    view.add_item(select)

    await interaction.response.send_message(
        "Choose your audible below:", view=view, ephemeral=False
    )

# Run the bot using your Railway environment variable
bot.run(os.environ["DISCORD_TOKEN"])
