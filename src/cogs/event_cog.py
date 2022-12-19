import discord
from discord.ext import tasks, commands
from src.discord_bot import DiscordBot
from src.utils.web_scraper import WebScraper
from src.services.event_service import EventService
from datetime import datetime, timedelta
import asyncio

class InfoCog(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self._bot = bot
        self.princess_connect_daily_update.start()
        self.dailyNotifications.start()
        self._eventService = EventService()

    def cog_unload(self):
        self.princess_connect_daily_update.cancel()
        self.dailyNotifications.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print("info cog is ready.")

    @commands.hybrid_group(name="event", pass_context=True, aliases=["events"])
    async def events(self, ctx: commands.context.Context):
        """
        This command sends the current event details within an embed message to the requester.
        :param ctx: the discord context of the message
        """
        try:
            results = await self._eventService.getCurrentEvents()

            if (not results):
                await ctx.send("There are no current events.")
                return

            embed = discord.embeds.Embed(title="Current Events", color=discord.Colour.blurple())
            for result in results:
                embed.add_field(name=f'{result["name"]}', value=f'{result["startDate"]} to {result["endDate"]}', inline= True)
            if (ctx.author):
                embed.set_footer(text=f'{ctx.author.name} requested this command.')
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            await ctx.send("Unable to get events.")
    
    @events.command(name="ending")
    async def events_ending(self, ctx: commands.context.Context, days:int=1):
        """
        This command sends the event details, that are ending, within an embed message to the requester.
        :param ctx: the discord context of the message
        :param days: the number of days
        """
        try:
            if (days <= 0):
                await ctx.send("Please provide a valid number of days.")
                return

            results = await self._eventService.getEventsEnding(days)

            if (not results):
                await ctx.send(f"There are no events ending within {days} {'days' if days > 1 else 'day'}.")
                return

            embed = discord.embeds.Embed(title="Events Ending", color=discord.Colour.blurple())
            for result in results:
                if (result["endDate"]):
                    embed.add_field(name=f'{result["name"]}', value=f'{result["startDate"]} to {result["endDate"]}\nEnding {result["endDateRelative"]}')
                else:
                    embed.add_field(name=f'{result["name"]}', value=f'Starting at {result["startDate"]}\n')
            if (ctx.author):
                embed.set_footer(text=f'{ctx.author.name} requested this command.')
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            await ctx.send("Unable to get events.")
    
    
    @events.command("upcoming")
    async def events_upcoming(self, ctx: commands.context.Context, days:int=1):
        """
        This command sends the upcoming event details within an embed message to the requester.
        :param ctx: the discord context of the message
        :param days: the number of days
        """
        try:
            if (days <= 0):
                await ctx.send("Please provide a valid number of days.")
                return

            results = await self._eventService.getEventsUpcoming(days)

            if (not results):
                await ctx.send(f"There are no future events within {days} {'days' if days > 1 else 'day'}.")
                return

            embed = discord.embeds.Embed(title="Upcoming Events", color=discord.Colour.blurple())
            for result in results:
                if (result["endDate"]):
                    embed.add_field(name=f'{result["name"]}', value=f'{result["startDate"]} to {result["endDate"]}\nStarting {result["startDateRelative"]}')
                else:
                    embed.add_field(name=f'{result["name"]}', value=f'Starting at {result["startDate"]}\nStarting {result["startDateRelative"]}')
            if (ctx.author):
                embed.set_footer(text=f'{ctx.author.name} requested this command.')
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            await ctx.send("Unable to get events.")

    
    @tasks.loop(hours=24.0)
    async def princess_connect_daily_update(self):
        """
        This task sends daily reminders of soon to be ending or upcoming events within the next 2 days.
        """

        print("Updating daily info.")
        try:
            print("Checking for expired events.")
            await self._eventService.cleanExpiredEvents()

            print("Webscraping crunchyroll princess connect news website.")
            events = await WebScraper.scrape_crunchyroll_events()
            if (events):
                print ("Checking if scraped data contains new events.")
                await self._eventService.addEvents(events)
        except Exception as e:
            print(e) 

    
    @tasks.loop(seconds=30)
    async def dailyNotifications(self):
        """
        This task sends daily reminders of soon to be ending or upcoming events within the next 2 days.
        """
        current_date = datetime.utcnow()

        # Sleep till expected time 14am UTC
        if (current_date >= current_date.replace(hour=14, minute=0, second=0, microsecond=0)):
            tomorrow = current_date + timedelta(days=1)
            tomorrow = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        else:
            tomorrow = current_date.replace(hour=14, minute=0, second=0, microsecond=0)

        seconds = (tomorrow - current_date).total_seconds()
        print(f"Daily reminder in: {seconds} seconds.")
        await asyncio.sleep(seconds)
        
        # Starting to print to every server
        print("Printing daily reminders.")
        await self._bot.wait_until_ready()

        # Get events ending and coming in 2 days
        eventsEnding = await self._eventService.getEventsEnding(days=2)
        eventsComing = await self._eventService.getEventsUpcoming(days=2)

        # Create embed of all event information
        embed = discord.embeds.Embed(title="Princess Connect Daily Update", color=discord.Colour.blurple())
        for event in eventsEnding:
            embed.add_field(name=f'{event["name"]}', value=f'Ending {event["endDateRelative"]}')
        for event in eventsComing:
            embed.add_field(name=f'{event["name"]}', value=f'Starting {event["startDateRelative"]}')

        # Print to every server if possible
        try:
            for guild in self._bot.guilds:
                channel = discord.utils.get(guild.text_channels, name='priconne-notifications')
                if (channel):
                    await channel.send(embed=embed)
        except Exception as e:
            print(e)
            print("Can't print")
    
    
    @princess_connect_daily_update.before_loop
    async def before_daily_update(self):
        """
        This method ensures the bot is fully setup before the daily update background task is done.
        """
        print("Waiting for bot to be ready before scraping data.")
        await self._bot.wait_until_ready()

async def setup(bot: DiscordBot):
    await bot.add_cog(InfoCog(bot=bot))