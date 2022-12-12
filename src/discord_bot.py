import os
import discord
from discord.ext import commands

class DiscordBot(commands.Bot):

    def __init__(self, command_prefix: str, intents: discord.Intents):
        commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents)
    
    async def setup_hook(self) -> None:
        # Load Cogs
        for filename in os.listdir("./src/cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f'src.cogs.{filename[:-3]}')
                print(filename, "loaded")

    async def on_ready(self) -> None:
        print(f'{self.user} is now running.')
    
    async def on_message(self, message: discord.message.Message) -> None:
        if message.author == self.user:
            return

        print(f'Message from {message.author}: {message.content}')

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')