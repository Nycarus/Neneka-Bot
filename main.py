import os
import discord
from dotenv import load_dotenv
import logging

from src.discord_bot import DiscordBot
from src.utils.logger import setup_logger

def main():
    # Load ENV data
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    # Intialize Bot
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True
    intents.emojis = True
    
    bot = DiscordBot(command_prefix=";", intents=intents)

    logger = setup_logger('discord', '/data/discord.log')

    # Run discord bot
    bot.run(TOKEN, root_logger=logger, log_level=logging.INFO)

if __name__ == '__main__':
    main()