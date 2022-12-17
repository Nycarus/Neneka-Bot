import discord
from discord.ext import tasks, commands
from src.discord_bot import DiscordBot
from src.utils.web_scraper import WebScraper
from src.services.event_service import EventService
from datetime import datetime, timedelta, time
import asyncio

class GuildCog(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self._bot = bot

    def cog_unload(self):
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        print("guild cog is ready.")
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            embed = discord.embeds.Embed(title="Hello!", description="Time to setup this bot to receive notifications.", color=discord.Colour.blurple())
            embed.add_field(name="Instructions:", 
            value=f"""
                - Use the command `;setup` to choose a channel where this bot will send messages to.\n
                - Alternatively, you may choose to create a #princess-connect-notification or priconne-notification channel to receive news.\n\n
                - Use `;help` to see a list of commands.
            """, inline=True)
            await guild.owner.send(embed=embed)
        except Exception as e:
            print(e)
            print(f'{guild.owner} has their dms turned off')

async def setup(bot: DiscordBot):
    await bot.add_cog(GuildCog(bot=bot))