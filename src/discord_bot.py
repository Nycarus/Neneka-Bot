import os
import discord
from discord.ext import commands
from src.utils.logger import setup_logger

class DiscordBot(commands.Bot):
    def __init__(self, command_prefix: str, intents: discord.Intents):
        commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents, help_command=None)
        self._logger = setup_logger('bot', '/data/discord.log')
    
    async def setup_hook(self):
        # Load Cogs
        for filename in os.listdir("./src/cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f'src.cogs.{filename[:-3]}')
                self._logger.info(f'{filename} cog loaded.')

    async def on_ready(self):
        print(f'{self.user} is now running.')
        self._logger.info(f'{self.user} is now running.')

    async def on_command_error(self, ctx: commands.context.Context, exception: commands.CommandError, /) -> None:
        await ctx.reply(f"Error has occured: {str(exception)}")