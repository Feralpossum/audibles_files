import discord
from discord.ext import commands
import os

# Bot setup
intents = discord.Intents.default()
intents.message_content = True  # Needed for slash commands to work properly

bot = commands.Bot(command_prefix="/", intents=intents)

# Your audible MP4s
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
}

# 🔥 Manual sync to your server
GUILD_ID = 1365585248259407922  # <- your real Server ID

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} slash commands to server {GUILD_ID}")
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
        embed.set_video(url=selected["url"])
        await interaction2.response.send_message(embed=embed)

    select.callback = select_callback

    view = discord.ui.View()
    view.add_item(select)

    await interaction.response.send_message(
        "Choose your audible below:", view=view, ephemeral=False
    )

# Run the bot
bot.run(os.environ["DISCORD_TOKEN"])
