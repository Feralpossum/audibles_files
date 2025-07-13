import os
import io
import asyncio
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands
from discord import FFmpegPCMAudio, PCMVolumeTransformer

# Load secrets
TOKEN    = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

# Where your raw files live
BASE_URL = "https://raw.githubusercontent.com/Feralpossum/audibles_files/main/Audibles"

# All your audibles (unchanged)
AUDIBLES = {
    "Boo": {"description": "Classic jump scare", "emoji": "🎃"},
    "DoneLosing": {"description": "Over it already", "emoji": "🏁"},
    "DontSlipMoppingFloor": {"description": "Careful... it's wet!", "emoji": "🧹"},
    # … all the rest of your entries …
    "nananana": {"description": "Nananana", "emoji": "🎵"},
}

# Bot setup
intents = discord.Intents.default()
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)


async def audible_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> list[app_commands.Choice[str]]:
    """Suggest audible names matching what the user has typed."""
    choices = [
        app_commands.Choice(name=name, value=name)
        for name in AUDIBLES
        if current.lower() in name.lower()
    ]
    return choices[:25]  # Discord only accepts up to 25 suggestions


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Sync failed: {e}")


@bot.tree.command(
    name="audible",
    description="Play an audible from the list",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(name="Start typing to search audibles")
@app_commands.autocomplete(name=audible_autocomplete)
async def audible(
    interaction: discord.Interaction,
    name: str
):
    """Fetch the selected audible and both post its video and play its audio in VC."""
    choice = name
    mp4_url = f"{BASE_URL}/{choice}.mp4"
    mp3_url = f"{BASE_URL}/{choice}.mp3"

    # give yourself time to fetch
    await interaction.response.defer()

    # 1) send the MP4 visual
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(mp4_url) as resp:
                if resp.status == 200:
                    buf = io.BytesIO(await resp.read())
                    await interaction.followup.send(
                        file=discord.File(buf, filename=f"{choice}.mp4")
                    )
                else:
                    await interaction.followup.send(
                        f"⚠️ Couldn’t fetch video for **{choice}** (HTTP {resp.status})"
                    )
    except Exception as e:
        await interaction.followup.send(f"❌ Video fetch error: {e}")

    # 2) join voice channel and autoplay the MP3
    if interaction.user.voice and interaction.user.voice.channel:
        vc = interaction.guild.voice_client or await interaction.user.voice.channel.connect()
        try:
            ffmpeg_opts = {
                "executable": "ffmpeg",
                "before_options": "-re -nostdin",
                "options": "-vn"
            }
            source = PCMVolumeTransformer(
                FFmpegPCMAudio(mp3_url, **ffmpeg_opts)
            )
            vc.play(source)
            while vc.is_playing():
                await asyncio.sleep(1)
            await vc.disconnect()
        except Exception as e:
            await interaction.followup.send(f"❌ Voice playback error: {e}")


bot.run(TOKEN)
