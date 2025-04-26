import discord
from discord.ext import commands
from discord import app_commands

class AudiblesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog loaded!")

    @app_commands.command(name="audible", description="Send an audible")
    async def audible(self, interaction: discord.Interaction):
        options = [
            discord.SelectOption(
                label="Boo",
                description="Classic jump scare",
                emoji="🎃"
            ),
            discord.SelectOption(
                label="ReallyLonelyBeingYou",
                description="A tragic roast",
                emoji="😢"
            ),
            discord.SelectOption(
                label="WelcomeExpectingYou",
                description="Warm fuzzy welcome",
                emoji="👋"
            )
        ]

        select = discord.ui.Select(
            placeholder="Choose your audible!",
            min_values=1,
            max_values=1,
            options=options
        )

        async def select_callback(interaction2: discord.Interaction):
            choice = select.values[0]
            urls = {
                "Boo": "https://audiblesfiles.vercel.app/Audibles/Boo.mp4",
                "ReallyLonelyBeingYou": "https://audiblesfiles.vercel.app/Audibles/ReallyLonelyBeingYou.mp4",
                "WelcomeExpectingYou": "https://audiblesfiles.vercel.app/Audibles/WelcomeExpectingYou.mp4"
            }
            url = urls.get(choice, "")
            embed = discord.Embed(
                title=f"🔊 {choice}",
                description="Here's your audible!",
                color=discord.Color.blue()
            )
            embed.set_video(url=url)
            await interaction2.response.send_message(embed=embed)

        select.callback = select_callback

        view = discord.ui.View()
        view.add_item(select)

        await interaction.response.send_message(
            "Choose your audible below:", view=view, ephemeral=False
        )

async def setup(bot):
    await bot.add_cog(AudiblesCog(bot))
