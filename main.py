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
    "Boo": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/Boo.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/Boo.mp3",
        "description": "Classic jump scare"
    },
    "DoneLosing": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp3",
        "description": "Over it already"
    },
    "DontSlipMoppingFloor": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp3",
        "description": "Careful... it's wet!"
    },
    "FatGuysNoMoney": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp3",
        "description": "Hard relatable moment"
    },
    "FromADrunkenMonkey": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/FromADrunkenMonkey.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/FromADrunkenMonkey.mp3",
        "description": "Monkey mayhem"
    },
    "GreatestEVER": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/GreatestEVER.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/GreatestEVER.mp3",
        "description": "All-time hype"
    },
    "INeverWinYouSuck": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/INeverWinYouSuck.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/INeverWinYouSuck.mp3",
        "description": "Ultimate sore loser"
    },
    "KeepPunching": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/KeepPunching.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/KeepPunching.mp3",
        "description": "Fight back!"
    },
    "LovesomeLovesomeNot": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/LovesomeLovesomeNot.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/LovesomeLovesomeNot.mp3",
        "description": "Love's a battlefield"
    },
    "Mmm_roar": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/Mmm_roar.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/Mmm_roar.mp3",
        "description": "Rawr means love"
    },
    "Mwahahaha": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/Mwahahaha.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/Mwahahaha.mp3",
        "description": "Evil laugh"
    },
    "NotEvenSameZipCodeFunny": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/NotEvenSameZipCodeFunny.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/NotEvenSameZipCodeFunny.mp3",
        "description": "You're not even close!"
    },
    "Pleasestandstill": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/Pleasestandstill.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/Pleasestandstill.mp3",
        "description": "Deer in headlights"
    },
    "ReallyLonelyBeingYou": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp3",
        "description": "A tragic roast"
    },
    "Sandwich": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/Sandwich.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/Sandwich.mp3",
        "description": "Sandwich"
    },
    "Score": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/Score.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/Score.mp3",
        "description": "Winning!"
    },
    "SeriouslyEvenTrying": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/SeriouslyEvenTrying.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/SeriouslyEvenTrying.mp3",
        "description": "Are you even trying?"
    },
    "ShakeLikeItDidntHurt": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/ShakeLikeItDidntHurt.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/ShakeLikeItDidntHurt.mp3",
        "description": "Shake it off"
    },
    "WelcomeExpectingYou": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp3",
        "description": "Grand entrance"
    },
    "Yawn": {
        "mp4": "https://audiblesfiles.vercel.app/Audibles/Yawn.mp4",
        "mp3": "https://audiblesfiles.vercel.app/Audibles/Yawn.mp3",
        "description": "So bored"
    },
}

class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, description=data["description"])
            for name, data in AUDIBLES.items()
        ]
        super().__init__(placeholder="Choose your audible!", options=options)

    async def callback(self, interaction: discord.Interaction):
        name = self.values[0]
        data = AUDIBLES[name]

        await interaction.response.defer()

        # Send MP4
        async with aiohttp.ClientSession() as session:
            async with session.get(data["mp4"]) as resp:
                if resp.status == 200:
                    mp4_data = io.BytesIO(await resp.read())
                    await interaction.followup.send(file=discord.File(mp4_data, filename=f"{name}.mp4"))
                else:
                    await interaction.followup.send(f"⚠️ Couldn't fetch MP4 (HTTP {resp.status})")

        # Join VC and play MP3
        if interaction.user.voice and interaction.user.voice.channel:
            vc = interaction.guild.voice_client
            if not vc:
                vc = await interaction.user.voice.channel.connect()

            async with aiohttp.ClientSession() as session:
                async with session.get(data["mp3"]) as resp:
                    if resp.status == 200:
                        mp3_data = await resp.read()
                    else:
                        await interaction.followup.send(f"⚠️ Couldn't fetch MP3 (HTTP {resp.status})")
                        return

            try:
                process = subprocess.Popen(
                    ["./ffmpeg", "-i", "pipe:0", "-f", "s16le", "-ar", "48000", "-ac", "2", "pipe:1"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE
                )
                process.stdin.write(mp3_data)
                process.stdin.close()

                audio = discord.PCMAudio(process.stdout)
                vc.play(audio)

                while vc.is_playing():
                    await asyncio.sleep(1)
                await vc.disconnect()
            except Exception as e:
                await interaction.followup.send(f"❌ Voice playback error:\n```{e}```")

class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())

@bot.event
async def on_ready():
    print(f"✅ Bot is ready: {bot.user}")
    await bot.tree.sync()
    bot.add_view(DropdownView())

@bot.tree.command(name="audible", description="Send and play an audible")
async def audible(interaction: discord.Interaction):
    await interaction.response.send_message("Choose your audible:", view=DropdownView())

if __name__ == "__main__":
    import sys
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN not set")
        sys.exit(1)
    bot.run(token)
