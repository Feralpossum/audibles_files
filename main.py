import discord
from discord.ext import commands
from discord import app_commands
import subprocess
import os
import aiohttp
from io import BytesIO

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")

AUDIBLES = {
    "Boo": {"url": "https://audiblesfiles.vercel.app/Audibles/Boo.mp4", "description": "Classic jump scare"},
    "DoneLosing": {"url": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp4", "description": "Over it already"},
    "DontSlipMoppingFloor": {"url": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp4", "description": "Careful... it's wet!"},
    "FatGuysNoMoney": {"url": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp4", "description": "Hard relatable moment"},
    "FromADrunkenMonkey": {"url": "https://audiblesfiles.vercel.app/Audibles/FromADrunkenMonkey.mp4", "description": "Monkey mayhem"},
    "GreatestEVER": {"url": "https://audiblesfiles.vercel.app/Audibles/GreatestEVER.mp4", "description": "All-time hype"},
    "INeverWinYouSuck": {"url": "https://audiblesfiles.vercel.app/Audibles/INeverWinYouSuck.mp4", "description": "Ultimate sore loser"},
    "KeepPunching": {"url": "https://audiblesfiles.vercel.app/Audibles/KeepPunching.mp4", "description": "Fight back!"},
    "LovesomeLovesomeNot": {"url": "https://audiblesfiles.vercel.app/Audibles/LovesomeLovesomeNot.mp4", "description": "Love's a battlefield"},
    "Mmm_roar": {"url": "https://audiblesfiles.vercel.app/Audibles/Mmm_roar.mp4", "description": "Rawr means love"},
    "Mwahahaha": {"url": "https://audiblesfiles.vercel.app/Audibles/Mwahahaha.mp4", "description": "Evil laugh"},
    "NotEvenSameZipCodeFunny": {"url": "https://audiblesfiles.vercel.app/Audibles/NotEvenSameZipCodeFunny.mp4", "description": "You're not even close!"},
    "Pleasestandstill": {"url": "https://audiblesfiles.vercel.app/Audibles/Pleasestandstill.mp4", "description": "Deer in headlights"},
    "ReallyLonelyBeingYou": {"url": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp4", "description": "A tragic roast"},
    "Sandwich": {"url": "https://audiblesfiles.vercel.app/Audibles/Sandwich.mp4", "description": "Time for lunch"},
    "Score": {"url": "https://audiblesfiles.vercel.app/Audibles/Score.mp4", "description": "Winning!"},
    "SeriouslyEvenTrying": {"url": "https://audiblesfiles.vercel.app/Audibles/SeriouslyEvenTrying.mp4", "description": "Are you even trying?"},
    "ShakeLikeItDidntHurt": {"url": "https://audiblesfiles.vercel.app/Audibles/ShakeLikeItDidntHurt.mp4", "description": "Shake it off"},
    "WelcomeExpectingYou": {"url": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp4", "description": "Grand entrance"},
    "Yawn": {"url": "https://audiblesfiles.vercel.app/Audibles/Yawn.mp4", "description": "So bored"}
}

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)
tree = client.tree

@client.event
async def on_ready():
    print(f"✅ Bot is ready: {client.user}")
    if GUILD_ID:
        synced = await tree.sync(guild=discord.Object(id=int(GUILD_ID)))
        print(f"✅ Synced {len(synced)} slash commands.")

@tree.command(name="ffmpeg_diagnose", description="Check if ffmpeg is executable.", guild=discord.Object(id=int(GUILD_ID)))
async def ffmpeg_diagnose(interaction: discord.Interaction):
    try:
        result = subprocess.run(["./ffmpeg", "-version"], capture_output=True, text=True, check=True)
        await interaction.response.send_message(f"`./ffmpeg` exists: True\nExecutable: True\nVersion: ```\n{result.stdout[:300]}...\n```")
    except Exception as e:
        await interaction.response.send_message(f"❌ ffmpeg check failed: ```\n{str(e)}\n```")

@tree.command(name="audible", description="Choose an audible to play", guild=discord.Object(id=int(GUILD_ID)))
@app_commands.describe(name="Name of the audible")
async def audible(interaction: discord.Interaction, name: str):
    await interaction.response.defer()
    audible = AUDIBLES.get(name)
    if not audible:
        await interaction.followup.send("❌ Audible not found.")
        return

    mp4_url = audible['url']
    mp3_url = mp4_url.replace(".mp4", ".mp3")
    
    await interaction.followup.send(f"**{name}**", file=discord.File(BytesIO(await fetch(mp4_url)), filename=f"{name}.mp4"))

    try:
        if interaction.user.voice and interaction.user.voice.channel:
            vc = await interaction.user.voice.channel.connect()
            async with aiohttp.ClientSession() as session:
                async with session.get(mp3_url) as resp:
                    if resp.status != 200:
                        raise Exception(f"Failed to fetch MP3: HTTP {resp.status}")
                    mp3_data = await resp.read()

            process = subprocess.Popen([
                "./ffmpeg", "-i", "pipe:0", "-f", "s16le", "-ar", "48000", "-ac", "2", "pipe:1"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

            audio_source = discord.PCMAudio(process.stdout)
            vc.play(audio_source)
            process.stdin.write(mp3_data)
            process.stdin.close()
            while vc.is_playing():
                await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=0.5))
            await vc.disconnect()
        else:
            await interaction.followup.send("⚠️ You're not in a voice channel!")
    except Exception as e:
        await interaction.followup.send(f"❌ Voice playback error:\n```\n{str(e)}\n```")

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.read()

client.run(TOKEN)
