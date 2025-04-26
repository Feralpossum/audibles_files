import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# Your audible MP4s hosted on Vercel
AUDIBLES = {
    "Boo": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Boo.mp4",
        "description": "Classic jump scare",
        "emoji": "🎃"
    },
    "WelcomeExpectingYou": {
        "url": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp4",
        "description": "Welcome announcement",
        "emoji": "👋"
    },
    "ReallyLonelyBeingYou": {
        "url": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp4",
        "description": "A tragic roast",
        "emoji": "😢"
    },
    # Add more here using the same format
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

    class Dropdown(discord.ui.Select):
        def __init__(self):
            super().__init__(
                placeholder="Choose an audible!",
                min_values=1,
                max_values=1,
                options=options
            )

        async def callback(self, interaction2: discord.Interaction):
            choice = self.values[0]
            url = AUDIBLES[choice]["url"]
            await interaction2.response.send_message(
                f"🔊 **{interaction2.user.display_name} sent an audible: {choice}!**\n{url}"
            )

    class DropdownView(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(Dropdown())

    await interaction.response.send_message(
        "Choose your audible below:",
        view=DropdownView(),
        ephemeral=False
    )

# Run the bot using your token from Railway env vars
import os
bot.run(os.environ["DISCORD_TOKEN"])
