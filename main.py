import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

tree = app_commands.CommandTree(discord.Client(intents=intents))
bot = commands.Bot(command_prefix="/", intents=intents)

# List of MP3 files and their URLs
SOUNDS = {
    "😮 Boo": "https://audiblesfiles.vercel.app/Audibles/Boo.mp3",
    "😡 DoneLosing": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp3",
    "⚡ DontSlipMoppingFloor": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp3",
    "💸 FatGuysNoMoney": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp3",
    "🦄 FromADrunkenMonkey": "https://audiblesfiles.vercel.app/Audibles/FromADrunkenMonkey.mp3",
    "🏆 GreatestEVER": "https://audiblesfiles.vercel.app/Audibles/GreatestEVER.mp3",
    "🙃 INeverWinYouSuck": "https://audiblesfiles.vercel.app/Audibles/INeverWinYouSuck.mp3",
    "🥊 KeepPunching": "https://audiblesfiles.vercel.app/Audibles/KeepPunching.mp3",
    "💕 LovesmeLovesmeNot": "https://audiblesfiles.vercel.app/Audibles/LovesmeLovesmeNot.mp3",
    "🌞 Mom": "https://audiblesfiles.vercel.app/Audibles/Mom.mp3",
}

class SoundSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, value=url)
            for name, url in SOUNDS.items()
        ]
        super().__init__(
            placeholder="Pick a sound to play...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        url = self.values[0]
        voice_channel = interaction.user.voice.channel
        if not voice_channel:
            await interaction.response.send_message("You must be in a voice channel first.", ephemeral=True)
            return

        vc = await voice_channel.connect()
        ffmpeg_audio = discord.FFmpegPCMAudio(
            url,
            executable="./ffmpeg",
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-f mp3 -vn"
        )
        vc.play(ffmpeg_audio)

        await interaction.response.send_message(f"🎵 Now playing: `{self.label}`")

        while vc.is_playing():
            await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=1))

        await vc.disconnect()

class SoundView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(SoundSelect())

@tree.command(name="audibles", description="Play a sound clip", guild=discord.Object(id=GUILD_ID))
async def audibles(interaction: discord.Interaction):
    await interaction.response.send_message("Pick a sound to play:", view=SoundView(), ephemeral=True)

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"✅ Logged in as {bot.user}")

bot.run(TOKEN)
