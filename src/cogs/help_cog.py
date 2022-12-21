import discord
from discord.ext import tasks, commands
import textwrap

from src.discord_bot import DiscordBot
from src.utils.logger import setup_logger

class HelpCog(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self._bot = bot
        self._logger = setup_logger('bot.cog.help', '/data/discord.log')

    @commands.Cog.listener()
    async def on_ready(self):
        self._logger.info("help cog is ready.")

    @commands.hybrid_command(name="help")
    async def help(self, ctx: commands.context.Context):
        message = textwrap.dedent(
            f"""
            __**User Commands**__
            **/event** - Displays current events.
            **/event upcoming** - Displays upcoming events.
            **/event ending** - Displays events ending.
            **/reminder** - Add a new reminder.
            **/reminder delete** - Delete all your reminders.
            
            __**Misc**__
            **/help** - Gets a list of commands.
            **/coinflip** - Flip a coin.
            **/random** - Chooses a number between 1 to X.
            **/should** - Ask a question, bot will give a vague answer. 

            __**Setting Commands**__
            **/setup** - Setup notification and ping role server settings.
            **/setup delete** - Delete server notification settings.
            """)
        embed = discord.embeds.Embed(title="Command List", description=message, color=discord.Colour.blurple())

        view = discord.ui.View()
        button = discord.ui.Button(style=discord.ButtonStyle.blurple, label="Github", url="https://github.com/Nycarus/Neneka-Bot")
        view.add_item(button)
        
        async with ctx.message.channel.typing():
            await ctx.reply(embed=embed, view=view)

async def setup(bot: DiscordBot):
    await bot.add_cog(HelpCog(bot=bot))