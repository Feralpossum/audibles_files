import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", 0))

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="/", intents=intents, application_id=1365552836200370217)
tree = bot.tree

SOUNDS = {
    "🚗 Boo": "https://audiblesfiles.vercel.app/Audibles/Boo.mp3",
    "🏆 DoneLosing": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp3",
    "🪨 DontSlipMoppingFloor": "https://audiblesfiles.vercel.app/Audibles/DontSlipMoppingFloor.mp3",
    "🛌 FatGuysNoMoney": "https://audiblesfiles.vercel.app/Audibles/FatGuysNoMoney.mp3"
}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Slash command '/audibles' registered ({len(synced)} commands)")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@tree.command(name="audibles", description="Play a sound", guild=discord.Object(id=GUILD_ID))
async def audibles(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("⚠️ Join a voice channel first.", ephemeral=True)
        return

    options = [
        discord.SelectOption(label=label, value=label)
        for label in SOUNDS.keys()
    ]

    class SoundSelect(discord.ui.Select):
        def __init__(self):
            super().__init__(
                placeholder="Choose a sound to play...",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, interaction: discord.Interaction):
            label = self.values[0]
            url = SOUNDS.get(label)
            if not url:
                await interaction.response.send_message("Sound not found.", ephemeral=True)
                return

            voice_channel = interaction.user.voice.channel
            vc = await voice_channel.connect()

            source = discord.FFmpegPCMAudio(url)
            vc.play(source)

            while vc.is_playing():
                await asyncio.sleep(1)

            await vc.disconnect()

    view = discord.ui.View()
    view.add_item(SoundSelect())
    await interaction.response.send_message("🎵 Pick a sound to play:", view=view, ephemeral=True)

bot.run(TOKEN)
