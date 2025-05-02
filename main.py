import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from dotenv import load_dotenv
from discord import FFmpegPCMAudio
from discord.ui import Select, View

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Define your MP3 files
MP3_SOUNDS = {
    "Boo": "https://audiblesfiles.vercel.app/Audibles/Boo.mp3",
    "DoneLosing": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp3",
    "DontSlipMoppingFloor": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp3",
    "FatGuysNoMoney": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp3"
}

class SoundSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, value=url, description=f"Play '{name}'")
            for name, url in MP3_SOUNDS.items()
        ]
        super().__init__(placeholder="Choose a sound to play...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        voice_channel = interaction.user.voice.channel
        if not voice_channel:
            await interaction.response.send_message("❗ Please join a voice channel first.", ephemeral=True)
            return

        # Reuse current voice client if already connected
        vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if vc and vc.is_connected():
            pass  # reuse existing connection
        else:
            vc = await voice_channel.connect()

        sound_url = self.values[0]
        source = FFmpegPCMAudio(sound_url)

        if vc.is_playing():
            vc.stop()

        vc.play(source)
        await interaction.response.send_message(f"🔊 Playing sound from: {sound_url}", ephemeral=True)

        while vc.is_playing():
            await asyncio.sleep(1)

        await vc.disconnect()

class SoundView(View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(SoundSelect())

@tree.command(name="audibles", description="Play an audible sound", guild=discord.Object(id=GUILD_ID))
async def audibles(interaction: discord.Interaction):
    await interaction.response.send_message("🎵 Choose a sound to play:", view=SoundView(), ephemeral=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Slash command '/audibles' registered ({len(synced)} commands)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

bot.run(TOKEN)
