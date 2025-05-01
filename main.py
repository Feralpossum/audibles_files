import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View
import asyncio
import aiohttp
import subprocess

TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"
GUILD_ID = 1365552836200370217  # Replace with your server ID

AUDIBLES = {
    "Boo": {"url": "https://audiblesfiles.vercel.app/Audibles/Boo.mp3", "description": "Classic jump scare"},
    "DoneLosing": {"url": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp3", "description": "Over it already"},
    "DontSlipMoppingFloor": {"url": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp3", "description": "Careful... it's wet!"},
    "FatGuysNoMoney": {"url": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp3", "description": "Hard relatable moment"},
    "FromADrunkenMonkey": {"url": "https://audiblesfiles.vercel.app/Audibles/FromADrunkenMonkey.mp3", "description": "Monkey mayhem"},
    "GreatestEVER": {"url": "https://audiblesfiles.vercel.app/Audibles/GreatestEVER.mp3", "description": "All-time hype"},
    "INeverWinYouSuck": {"url": "https://audiblesfiles.vercel.app/Audibles/INeverWinYouSuck.mp3", "description": "Ultimate sore loser"},
    "KeepPunching": {"url": "https://audiblesfiles.vercel.app/Audibles/KeepPunching.mp3", "description": "Fight back!"},
    "LovesomeLovesomeNot": {"url": "https://audiblesfiles.vercel.app/Audibles/LovesomeLovesomeNot.mp3", "description": "Love's a battlefield"},
    "Mmm_roar": {"url": "https://audiblesfiles.vercel.app/Audibles/Mmm_roar.mp3", "description": "Rawr means love"},
    "Mwahahaha": {"url": "https://audiblesfiles.vercel.app/Audibles/Mwahahaha.mp3", "description": "Evil laugh"},
    "NotEvenSameZipCodeFunny": {"url": "https://audiblesfiles.vercel.app/Audibles/NotEvenSameZipCodeFunny.mp3", "description": "You're not even close!"},
    "Pleasestandstill": {"url": "https://audiblesfiles.vercel.app/Audibles/Pleasestandstill.mp3", "description": "Deer in headlights"},
    "ReallyLonelyBeingYou": {"url": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp3", "description": "A tragic roast"},
    "Sandwich": {"url": "https://audiblesfiles.vercel.app/Audibles/Sandwich.mp3", "description": "Time for lunch"},
    "Score": {"url": "https://audiblesfiles.vercel.app/Audibles/Score.mp3", "description": "Winning!"},
    "SeriouslyEvenTrying": {"url": "https://audiblesfiles.vercel.app/Audibles/SeriouslyEvenTrying.mp3", "description": "Are you even trying?"},
    "ShakeLikeItDidntHurt": {"url": "https://audiblesfiles.vercel.app/Audibles/ShakeLikeItDidntHurt.mp3", "description": "Shake it off"},
    "WelcomeExpectingYou": {"url": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp3", "description": "Grand entrance"},
    "Yawn": {"url": "https://audiblesfiles.vercel.app/Audibles/Yawn.mp3", "description": "So bored"}
}

intents = discord.Intents.default()
intents.message_content = False
bot = commands.Bot(command_prefix="!", intents=intents)

def get_ffmpeg_executable():
    return "./ffmpeg"

class AudibleSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=key, description=value["description"][:100])
            for key, value in AUDIBLES.items()
        ]
        super().__init__(
            placeholder="Choose an audible...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        url = AUDIBLES[selected]["url"]

        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ You must be in a voice channel!", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel
        vc = await voice_channel.connect()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await interaction.response.send_message(f"❌ Could not fetch {selected}", ephemeral=True)
                        return

                    mp3_data = await resp.read()

            ffmpeg_exe = get_ffmpeg_executable()
            process = subprocess.Popen([
                ffmpeg_exe, "-i", "pipe:0", "-f", "s16le", "-ar", "48000", "-ac", "2", "pipe:1"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

            process.stdin.write(mp3_data)
            process.stdin.close()

            audio = discord.FFmpegPCMAudio(process.stdout)
            vc.play(audio)

            await interaction.response.send_message(f"🔊 Playing: {selected}", ephemeral=True)

            while vc.is_playing():
                await asyncio.sleep(1)

        finally:
            await vc.disconnect()

class DropdownView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(AudibleSelect())

@bot.event
async def on_ready():
    print(f"✅ Bot is ready: {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

@bot.tree.command(name="audibles", description="Play an audible")
async def audibles(interaction: discord.Interaction):
    await interaction.response.send_message("Select an audible to play:", view=DropdownView(), ephemeral=True)

bot.run(TOKEN)
