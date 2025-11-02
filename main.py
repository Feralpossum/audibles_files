import asyncio
import discord
import subprocess
import os

TOKEN    = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.voice_states = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    guild = bot.get_guild(GUILD_ID)
    print(f"Guild found: {guild.name if guild else 'None'}")

    # ffmpeg check
    try:
        print("=== ffmpeg check ===")
        out = subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.STDOUT, text=True)
        print(out.splitlines()[0])
    except Exception as e:
        print("ffmpeg check failed:", e)

    # opus check
    print("=== opus check ===")
    try:
        if not discord.opus.is_loaded():
            discord.opus.load_opus("libopus.so.0")
        print("Opus loaded:", discord.opus.is_loaded())
    except Exception as e:
        print("Opus load failed:", e)

    print("=== UDP test ===")
    # Try connecting to a dummy voice channel if one exists
    for ch in guild.voice_channels:
        print(f"Attempting voice connect test to: {ch.name} ({ch.id})")
        try:
            vc = await ch.connect(timeout=15, reconnect=False, self_deaf=False)
            print("✅ Voice connect SUCCESS:", ch.name)
            await asyncio.sleep(1)
            await vc.disconnect(force=True)
            print("✅ UDP path confirmed OK")
            break
        except Exception as e:
            print("❌ Voice connect FAILED:", e)
    print("All done. Exiting.")
    await bot.close()

bot.run(TOKEN)
