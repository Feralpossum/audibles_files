import discord
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

# Dictionary of audibles
AUDIBLES = {
    "Boo": "https://audiblesfiles.vercel.app/Audibles/Boo.mp4",
    # Add more audibles here
}

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

@bot.command()
async def audible(ctx, *, name: str):
    url = AUDIBLES.get(name)
    if url:
        await ctx.send(f"{ctx.author.mention} sent an audible: {name}!", file=discord.File(url))
    else:
        await ctx.send("Audible not found.")
