import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import io
import os

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # Needed for joining voice channels
bot = commands.Bot(command_prefix="/", intents=intents)

# Your 20 audible MP4s and matching MP3s
AUDIBLES = {
    "Boo": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Boo.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/Boo.mp3",
        "description": "Classic jump scare",
        "emoji": "🎃"
    },
    "DoneLosing": {
        "url": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/DoneLosing.mp3",
        "description": "Over it already",
        "emoji": "🏁"
    },
    # ... (repeat for all 20 audibles)
    "WelcomeExpectingYou": {
        "url": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp3",
        "description": "Grand entrance",
        "emoji": "🎉"
    },
    "Yawn": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Yawn.mp4",
        "audio": "https://audiblesfiles.vercel.app/Audibles/Yawn.mp3",
        "description": "So bored",
        "emoji": "🥱"
    }
}

# Dropdown selection class
class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=name,
                description=data["description"],
                emoji=data.get("emoji")
            )
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
        audible = AUDIBLES[choice]
        mp4_url = audible["url"]
        mp3_url = audible.get("audio")

        await interaction.response.defer()

        # Try to join voice channel if user is in one
        if interaction.user.voice and mp3_url:
            vc = await interaction.user.voice.channel.connect()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(mp3_url) as resp:
                        if resp.status != 200:
                            await interaction.followup.send('Could not download audio file.', ephemeral=True)
                            return
                        data = io.BytesIO(await resp.read())

                audio_source = discord.FFmpegPCMAudio(data, pipe=True)
                vc.play(audio_source)

                # Auto disconnect after sound is finished
                while vc.is_playing():
                    await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=1))
                await vc.disconnect()

            except Exception as e:
                print(f"Voice playback error: {e}")
                await vc.disconnect()

        # Send the MP4 file visually to the text chat
        async with aiohttp.ClientSession() as session:
            async with session.get(mp4_url) as resp:
                if resp.status != 200:
                    await interaction.followup.send('Could not download video file.', ephemeral=True)
                    return
                data = io.BytesIO(await resp.read())

        file = discord.File(data, filename=f"{choice}.mp4")

        await interaction.followup.send(file=file)

# Dropdown view class
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())

# Bot startup event
@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    bot.add_view(DropdownView())

# Slash command
@bot.tree.command(name="audible", description="Send an audible from the list")
async def audible(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Choose your audible below:",
        view=DropdownView(),
        ephemeral=False
    )

# Run bot
bot.run(os.environ["DISCORD_TOKEN"])
