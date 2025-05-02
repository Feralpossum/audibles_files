import os
import discord
import asyncio
import requests
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path

# Environment setup
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))

# Vercel-hosted MP3s
AUDIBLES = {
    "Boo": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Boo.mp3",
        "emoji": "👻",
        "description": "A spooky boo!"
    },
    "Fart": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Fart.mp3",
        "emoji": "💨",
        "description": "Classic comedic timing"
    },
    "Wow": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Wow.mp3",
        "emoji": "😲",
        "description": "Astonishing!"
    },
    "Horn": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Horn.mp3",
        "emoji": "📣",
        "description": "Airhorn madness"
    }
}

# Ensure audio folder
Path("audio").mkdir(exist_ok=True)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

class SoundSelect(discord.ui.Select):
    def __init__(self, vc: discord.VoiceClient):
        self.vc = vc
        options = [
            discord.SelectOption(
                label=name,
                description=meta["description"],
                emoji=meta["emoji"],
                value=name
            )
            for name, meta in AUDIBLES.items()
        ]
        super().__init__(placeholder="Pick a sound to play...", options=options)

    async def callback(self, interaction: discord.Interaction):
        sound_name = self.values[0]
        url = AUDIBLES[sound_name]["url"]
        filename = f"audio/{sound_name}.mp3"
        try:
            if not os.path.exists(filename):
                await interaction.followup.send(f"⬇️ Downloading `{sound_name}`...", ephemeral=True)
                r = requests.get(url)
                r.raise_for_status()
                with open(filename, "wb") as f:
                    f.write(r.content)

            if self.vc.is_playing():
                self.vc.stop()

            self.vc.play(
                discord.FFmpegPCMAudio(filename),
                after=lambda e: asyncio.run_coroutine_threadsafe(self.vc.disconnect(), bot.loop)
            )

            await interaction.response.send_message(f"🔊 Playing: **{sound_name}**", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error playing sound: {e}", ephemeral=True)

class SoundView(discord.ui.View):
    def __init__(self, vc: discord.VoiceClient):
        super().__init__(timeout=180)
        self.add_item(SoundSelect(vc))

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Slash command '/audibles' registered ({len(synced)} commands)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")
    print(f"✅ Logged in as {bot.user}")

@bot.tree.command(name="audibles", description="Play a sound", guild=discord.Object(id=GUILD_ID))
async def audibles(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❗ Join a voice channel first.", ephemeral=True)
        return

    try:
        vc = await interaction.user.voice.channel.connect()
        await interaction.response.send_message("🎵 Choose a sound:", view=SoundView(vc), ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Could not join channel: {e}", ephemeral=True)

bot.run(TOKEN)
