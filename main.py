import os
import discord
from dotenv import load_dotenv
import logging

from src.discord_bot import DiscordBot

def main():
    # Load ENV data
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    # Intialize Bot
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True
    bot = DiscordBot(command_prefix=";", intents=intents)

    # Setup logging
    log_handler = logging.FileHandler(filename='/data/discord.log', encoding='utf-8', mode='w')

    # Run discord bot
    bot.run(TOKEN, log_handler=log_handler, log_level=logging.DEBUG)

if __name__ == '__main__':
    main()