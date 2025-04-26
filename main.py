import discord
from discord.ext import commands
import os

# Set up the bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

GUILD_ID = 1365585248259407922  # Your Discord server ID

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} slash commands to server {GUILD_ID}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

async def load_extensions():
    await bot.load_extension("audibles_cog")  # Load your cog file

bot.run(os.environ["DISCORD_TOKEN"])
