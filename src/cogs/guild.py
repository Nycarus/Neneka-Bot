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
    async def on_guild_join(self, guild: discord.guild.Guild):
        try:
            embed = discord.embeds.Embed(title="Hello!", description="Time to setup this bot to receive notifications.", color=discord.Colour.blurple())
            embed.add_field(name="Instructions:", inline=True,
            value=
            f"""
            - Use the command `;setup #notification-channel #bot-command-channel` to choose channels where this bot will send messages to.
            - Alternatively, you may choose to create a `#princess-connect-notification` or `#priconne-notification` channel to receive notifications.

            - Use `;help` to see a list of commands.
            """)
            await guild.owner.send(embed=embed)
        except Exception as e:
            print(e)
            print(f'{guild.owner} has their dms turned off')

    @commands.hybrid_command(name="setup")
    async def setup(self, ctx: commands.context.Context, notificationChannel:discord.TextChannel = None, commandChannel:discord.TextChannel = None):
        # prevent people from using this command if they are not owner or admin
        if (not (ctx.author.guild_permissions.administrator or ctx.author == ctx.guild.owner)):
            ctx.send("You do not have permission to use this command.")
        
        # TODO: add a way to Update guild settings


async def setup(bot: DiscordBot):
    await bot.add_cog(GuildCog(bot=bot))