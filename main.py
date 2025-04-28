import discord
from discord.ext import commands
from discord import app_commands
import os

# Bot setup
intents = discord.Intents.default()
intents.message_content = True  # Fix for Discord message content warning
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
            custom_id="audible_dropdown"  # Required for persistence
        )

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        url = AUDIBLES[choice]["url"]
        await interaction.response.send_message(
            f"🔊 **{interaction.user.display_name} sent an audible: {choice}!**\n{url}"
        )

# Dropdown view class
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Required for persistence
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

    # Register the persistent DropdownView globally
    bot.add_view(DropdownView())

# Slash command to trigger audibles
@bot.tree.command(name="audible", description="Send an audible from the list")
async def audible(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Choose your audible below:",
        view=DropdownView(),  # Fresh view per interaction
        ephemeral=False
    )

# Run the bot using Railway environment variable
bot.run(os.environ["DISCORD_TOKEN"])
