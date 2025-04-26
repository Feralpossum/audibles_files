import discord
from discord.ext import commands
import asyncio
import os

# Bot setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

async def main():
    await bot.load_extension("audibles_cog")
    await bot.start(os.environ["DISCORD_TOKEN"])

asyncio.run(main())
