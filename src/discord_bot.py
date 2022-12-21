import os
import discord
from discord.ext import commands
import logging

class DiscordBot(commands.Bot):
    def __init__(self, command_prefix: str, intents: discord.Intents):
        commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents)
    
    async def setup_hook(self):
        # Load Cogs
        for filename in os.listdir("./src/cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f'src.cogs.{filename[:-3]}')
                logging.info(f'{filename} cog loaded.')

    async def on_ready(self):
        print(f'{self.user} is now running.')