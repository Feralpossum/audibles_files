import os
import sys

print("✅ Reached main.py", flush=True)
print("📦 Checking environment variables...", flush=True)

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

print(f"🔑 DISCORD_BOT_TOKEN is: {'set' if TOKEN else 'NOT SET'}", flush=True)
print(f"🆔 GUILD_ID is: {GUILD_ID}", flush=True)

if not TOKEN or not GUILD_ID:
    print("❌ ERROR: Missing DISCORD_BOT_TOKEN or GUILD_ID", flush=True)
    sys.exit(1)

print("✅ main.py finished successfully", flush=True)
