import os
import discord
from dotenv import load_dotenv

from src.discord_bot import DiscordBot

def main():
    # Load ENV data
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    # Intialize Bot
    intents = discord.Intents.default()
    intents.message_content = True
    bot = DiscordBot(command_prefix="!", intents=intents)

    bot.run(TOKEN)

if __name__ == '__main__':
    main()