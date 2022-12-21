import discord
from discord.ext import tasks, commands
import textwrap

from src.discord_bot import DiscordBot

class HelpCog(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self._bot = bot

    @commands.hybrid_command(name="help")
    async def help(self, ctx: commands.context.Context):
        message = textwrap.dedent(
            f"""
            __**User Commands**__
            **/event** - Displays current events.
            **/event upcoming** - Displays upcoming events.
            **/event ending** - Displays events ending.
            **/reminder** - Add a new reminder
            **/reminder delete** - Delete all your reminders.
            **/help** - Gets a list of commands.

            __**Setting Commands**__
            **/setup** - Setup notification and ping role server settings
            **/setup delete** - Delete server settings
            """)
        embed = discord.embeds.Embed(title="Command List", description=message, color=discord.Colour.blurple())

        view = discord.ui.View()
        button = discord.ui.Button(style=discord.ButtonStyle.blurple, label="Github", url="https://github.com/Nycarus/Neneka-Bot")
        view.add_item(button)
        
        await ctx.reply(embed=embed, view=view)

async def setup(bot: DiscordBot):
    await bot.add_cog(HelpCog(bot=bot))