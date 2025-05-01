import discord
from discord.ext import commands
import aiohttp
import asyncio
import io
import os
import subprocess

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="/", intents=intents)

AUDIBLES = {
    "Boo": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/Boo.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Boo.mp3", "description": "Classic jump scare"},
    "DoneLosing": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp3", "description": "Over it already"},
    "DontSlipMoppingFloor": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp3", "description": "Careful... it's wet!"},
    "FatGuysNoMoney": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp3", "description": "Hard relatable moment"},
    "FromADrunkenMonkey": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/FromADrunkenMonkey.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/FromADrunkenMonkey.mp3", "description": "Monkey mayhem"},
    "GreatestEVER": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/GreatestEVER.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/GreatestEVER.mp3", "description": "All-time hype"},
    "INeverWinYouSuck": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/INeverWinYouSuck.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/INeverWinYouSuck.mp3", "description": "Ultimate sore loser"},
    "KeepPunching": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/KeepPunching.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/KeepPunching.mp3", "description": "Fight back!"},
    "LovesomeLovesomeNot": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/LovesomeLovesomeNot.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/LovesomeLovesomeNot.mp3", "description": "Love's a battlefield"},
    "Mmm_roar": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/Mmm_roar.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Mmm_roar.mp3", "description": "Rawr means love"},
    "Mwahahaha": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/Mwahahaha.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Mwahahaha.mp3", "description": "Evil laugh"},
    "NotEvenSameZipCodeFunny": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/NotEvenSameZipCodeFunny.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/NotEvenSameZipCodeFunny.mp3", "description": "You're not even close!"},
    "Pleasestandstill": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/Pleasestandstill.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Pleasestandstill.mp3", "description": "Deer in headlights"},
    "ReallyLonelyBeingYou": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp3", "description": "A tragic roast"},
    "Sandwich": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/Sandwich.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Sandwich.mp3", "description": "Time for lunch"},
    "Score": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/Score.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Score.mp3", "description": "Winning!"},
    "SeriouslyEvenTrying": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/SeriouslyEvenTrying.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/SeriouslyEvenTrying.mp3", "description": "Are you even trying?"},
    "ShakeLikeItDidntHurt": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/ShakeLikeItDidntHurt.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/ShakeLikeItDidntHurt.mp3", "description": "Shake it off"},
    "WelcomeExpectingYou": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp3", "description": "Grand entrance"},
    "Yawn": {"mp4_url": "https://audiblesfiles.vercel.app/Audibles/Yawn.mp4", "mp3_url": "https://audiblesfiles.vercel.app/Audibles/Yawn.mp3", "description": "So bored"},
}

class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, description=data["description"])
            for name, data in AUDIBLES.items()
        ]
        super().__init__(placeholder="Choose your audible!", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        mp4_url = AUDIBLES[choice]["mp4_url"]
        mp3_url = AUDIBLES[choice]["mp3_url"]

        await interaction.response.defer()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(mp4_url) as resp:
                    if resp.status == 200:
                        mp4_data = io.BytesIO(await resp.read())
                        await interaction.followup.send(file=discord.File(mp4_data, filename=f"{choice}.mp4"))
                    else:
                        await interaction.followup.send(f"⚠️ Couldn't fetch MP4 for `{choice}` (HTTP {resp.status})")
        except Exception as e:
            await interaction.followup.send(f"❌ MP4 error: {e}")

        if interaction.user.voice and interaction.user.voice.channel:
            try:
                vc = interaction.guild.voice_client
                if not vc or not vc.is_connected():
                    vc = await interaction.user.voice.channel.connect()

                async with aiohttp.ClientSession() as session:
                    async with session.get(mp3_url) as resp:
                        if resp.status != 200:
                            await interaction.followup.send(f"⚠️ Couldn't fetch MP3 (HTTP {resp.status})")
                            return
                        mp3_data = await resp.read()

                # Convert MP3 to PCM and buffer it into memory
                ffmpeg = subprocess.Popen(
                    ["./ffmpeg", "-i", "pipe:0", "-f", "s16le", "-ar", "48000", "-ac", "2", "pipe:1"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE
                )
                pcm_audio, _ = ffmpeg.communicate(input=mp3_data)

                # Stream audio from memory
                audio = discord.PCMAudio(io.BytesIO(pcm_audio))

                def after_playing(error):
                    print(f"🎧 Playback finished or error: {error}")
                    coro = vc.disconnect()
                    asyncio.run_coroutine_threadsafe(coro, bot.loop)

                vc.play(audio, after=after_playing)

            except Exception as e:
                await interaction.followup.send(f"❌ Voice playback error:\n```{e}```")

class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())

@bot.tree.command(name="audible", description="Send and play an audible")
async def audible(interaction: discord.Interaction):
    await interaction.response.send_message("Choose your audible:", view=DropdownView())

@bot.tree.command(name="ffmpeg_diagnose", description="Test if ffmpeg is working")
async def ffmpeg_diagnose(interaction: discord.Interaction):
    try:
        exists = os.path.isfile("./ffmpeg")
        executable = os.access("./ffmpeg", os.X_OK)
        output = subprocess.check_output(["./ffmpeg", "-version"]).decode("utf-8").splitlines()[0] if exists and executable else "N/A"

        await interaction.response.send_message(
            f"✔️ ./ffmpeg exists: `{exists}`\n"
            f"✔️ Executable: `{executable}`\n"
            f"🔍 Version: `{output}`"
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ ffmpeg diagnose error:\n```{e}```")

@bot.event
async def on_ready():
    print(f"✅ Bot is ready: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Sync error: {e}")
    bot.add_view(DropdownView())

async def main():
    await bot.start(os.environ["DISCORD_TOKEN"])

asyncio.run(main())

