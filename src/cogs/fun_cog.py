import discord
from discord.ext import tasks, commands
import textwrap
import random

from src.discord_bot import DiscordBot
from src.utils.logger import setup_logger

class FunCog(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self._bot = bot
        self._logger = setup_logger('bot.cog.fun', '/data/discord.log')

    @commands.Cog.listener()
    async def on_ready(self):
        self._logger.info("fun cog is ready.")

    @commands.hybrid_command(name="coinflip", description="Does a coin flip.")
    async def coinflip(self, ctx: commands.context.Context):
        flip = random.randint(1,2)
        async with ctx.message.channel.typing():
            await ctx.reply("Heads." if flip == 1 else "Tails.")

    @commands.hybrid_command(name="random", description="Choose a number between 1 to max number.")
    async def random(self, ctx: commands.context.Context, number:int = commands.parameter(default=100, description="The max random number.")):
        if (number <= 1 or number > 999999):
            async with ctx.message.channel.typing():
                await ctx.reply("Choose a number higher than 1, but lower or equals to 999999")
            return
        result = random.randint(1, number)
        async with ctx.message.channel.typing():
            await ctx.reply(f"{result} out of {number}.")

    @commands.hybrid_command(name="should", description="Ask the bot for random answers.")
    async def should(self, ctx: commands.context.Context, *, description = commands.parameter(default=None, description="Question.")):
        if (not description):
            async with ctx.message.channel.typing():
                await ctx.reply("Add a description.")
            return

        result = random.randint(1, 10)

        if (result == 9 or result == 10):
            message = "Maybe."
        elif (result <= 8 or result >= 5):
            message = "Yes."
        else:
            message = "No."
            
        async with ctx.message.channel.typing():
            await ctx.reply(message)

async def setup(bot: DiscordBot):
    await bot.add_cog(FunCog(bot=bot))