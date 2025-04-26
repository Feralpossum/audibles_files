import discord
from discord import app_commands
from discord.ext import commands

AUDIBLES = {
    "Boo": {
        "url": "https://audiblesfiles.vercel.app/Audibles/Boo.mp4",
        "description": "Classic jump scare",
        "emoji": "🎃"
    },
    "ReallyLonelyBeingYou": {
        "url": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp4",
        "description": "A tragic roast",
        "emoji": "😢"
    },
    "WelcomeExpectingYou": {
        "url": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp4",
        "description": "Warm fuzzy welcome",
        "emoji": "👋"
    },
}

class Audibles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="audible", description="Send an audible from the list")
    async def audible(self, interaction: discord.Interaction):
        options = [
            discord.SelectOption(
                label=name,
                description=data["description"],
                emoji=data.get("emoji", None)
            )
            for name, data in AUDIBLES.items()
        ]

        select = discord.ui.Select(
            placeholder="Choose your audible!",
            min_values=1,
            max_values=1,
            options=options
        )

        async def select_callback(interaction2: discord.Interaction):
            choice = select.values[0]
            selected = AUDIBLES[choice]
            embed = discord.Embed(
                title=f"🔊 {choice}",
                description=selected["description"],
                color=discord.Color.blue()
            )
            embed.set_video(url=selected["url"])
            await interaction2.response.send_message(embed=embed)

        select.callback = select_callback

        view = discord.ui.View()
        view.add_item(select)

        await interaction.response.send_message(
            "Choose your audible below:", view=view, ephemeral=False
        )

async def setup(bot):
    await bot.add_cog(Audibles(bot))
