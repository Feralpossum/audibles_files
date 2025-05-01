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
    "Boo": {"url": "https://audiblesfiles.vercel.app/Audibles/Boo", "description": "Classic jump scare"},
    "DoneLosing": {"url": "https://audiblesfiles.vercel.app/Audibles/DoneLosing", "description": "Over it already"},
    "DontSlipMoppingFloor": {"url": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor", "description": "Careful... it's wet!"},
    "FatGuysNoMoney": {"url": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney", "description": "Hard relatable moment"},
    "FromADrunkenMonkey": {"url": "https://audiblesfiles.vercel.app/Audibles/FromADrunkenMonkey", "description": "Monkey mayhem"},
    "GreatestEVER": {"url": "https://audiblesfiles.vercel.app/Audibles/GreatestEVER", "description": "All-time hype"},
    "INeverWinYouSuck": {"url": "https://audiblesfiles.vercel.app/Audibles/INeverWinYouSuck", "description": "Ultimate sore loser"},
    "KeepPunching": {"url": "https://audiblesfiles.vercel.app/Audibles/KeepPunching", "description": "Fight back!"},
    "LovesomeLovesomeNot": {"url": "https://audiblesfiles.vercel.app/Audibles/LovesomeLovesomeNot", "description": "Love's a battlefield"},
    "Mmm_roar": {"url": "https://audiblesfiles.vercel.app/Audibles/Mmm_roar", "description": "Rawr means love"},
    "Mwahahaha": {"url": "https://audiblesfiles.vercel.app/Audibles/Mwahahaha", "description": "Evil laugh"},
    "NotEvenSameZipCodeFunny": {"url": "https://audiblesfiles.vercel.app/Audibles/NotEvenSameZipCodeFunny", "description": "You're not even close!"},
    "Pleasestandstill": {"url": "https://audiblesfiles.vercel.app/Audibles/Pleasestandstill", "description": "Deer in headlights"},
    "ReallyLonelyBeingYou": {"url": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou", "description": "A tragic roast"},
    "Sandwich": {"url": "https://audiblesfiles.vercel.app/Audibles/Sandwich", "description": "Time for lunch"},
    "Score": {"url": "https://audiblesfiles.vercel.app/Audibles/Score", "description": "Winning!"},
    "SeriouslyEvenTrying": {"url": "https://audiblesfiles.vercel.app/Audibles/SeriouslyEvenTrying", "description": "Are you even trying?"},
    "ShakeLikeItDidntHurt": {"url": "https://audiblesfiles.vercel.app/Audibles/ShakeLikeItDidntHurt", "description": "Shake it off"},
    "WelcomeExpectingYou": {"url": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou", "description": "Grand entrance"},
    "Yawn": {"url": "https://audiblesfiles.vercel.app/Audibles/Yawn", "description": "So bored"}
}

class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, description=data["description"])
            for name, data in AUDIBLES.items()
        ]
        super().__init__(
            placeholder="Choose your audible!",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="audible_dropdown"
        )

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        base_url = AUDIBLES[choice]["url"]
        mp4_url = f"{base_url}.mp4"
        mp3_url = f"{base_url}.mp3"

        await interaction.response.defer()

        # Send MP4
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(mp4_url) as resp:
                    if resp.status == 200:
                        mp4_data = io.BytesIO(await resp.read())
                        await interaction.followup.send(file=discord.File(mp4_data, filename=f"{choice}.mp4"))
                    else:
                        await interaction.followup.send(f"⚠️ Couldn't fetch MP4 for `{choice}` (HTTP {resp.status})")
        except Exception as e:
            await interaction.followup.send(f"❌ Error fetching MP4: {e}")

        # Play MP3 in voice
        if interaction.user.voice and interaction.user.voice.channel:
            try:
                vc = interaction.guild.voice_client
                if not vc:
                    vc = await interaction.user.voice.channel.connect()

                async with aiohttp.ClientSession() as session:
                    async with session.get(mp3_url) as resp:
                        if resp.status != 200:
                            await interaction.followup.send(f"⚠️ Couldn't fetch MP3 (HTTP {resp.status})")
                            return
                        mp3_data = await resp.read()

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
                await interaction.followup.send(f"❌ Voice playback error:\n```\n{e}\n```")

class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())

@bot.event
async def on_ready():
    print(f"✅ Bot is ready: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Sync error: {e}")
    try:
        bot.add_view(DropdownView())
    except Exception as e:
        print(f"❌ View error: {e}")

@bot.tree.command(name="audible", description="Send and play an audible")
async def audible(interaction: discord.Interaction):
    await interaction.response.send_message("Choose your audible:", view=DropdownView())

# Run bot
if __name__ == "__main__":
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN not set in environment.")
    bot.run(TOKEN)
