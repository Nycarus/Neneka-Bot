import discord
from discord.ext import tasks, commands
from src.discord_bot import DiscordBot
from src.utils.web_scraper import WebScraper
from src.services.event_service import EventService
from src.cogs.guild_cog import GuildCog
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

    @commands.hybrid_group(name="event", description="Get events.", pass_context=True, aliases=["events"])
    async def events(self, ctx: commands.context.Context):
        """
        This command sends the current event details within an embed message to the requester.
        :param ctx: the discord context of the message
        """
        try:
            results = await self._eventService.getCurrentEvents()

            if (not results):
                await ctx.reply("There are no current events.")
                return

            embed = self.createEventEmbed(ctx=ctx, title="Current Events", data=results, days=None, relative="endDate")
            
            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)
            await ctx.reply("Unable to get events.")
    
    @events.command(name="ending", description="Get events ending soon.")
    async def events_ending(self, ctx: commands.context.Context, days:int=1):
        """
        This command sends the event details, that are ending, within an embed message to the requester.
        :param ctx: the discord context of the message
        :param days: the number of days
        """
        try:
            if (type(days) != int or days <= 0):
                await ctx.reply("Please provide a valid number of days.")
                return

            results = await self._eventService.getEventsEnding(days)

            if (not results):
                await ctx.reply(f"There are no events ending within {days} {'days' if days > 1 else 'day'}.")
                return

            embed = self.createEventEmbed(ctx=ctx, title="Events Ending", data=results, days=days, relative="endDate")
            
            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)
            await ctx.reply("Unable to get events.")
    
    @events.command(name="upcoming", description="Get upcoming events.")
    async def events_upcoming(self, ctx: commands.context.Context, days:int=1):
        """
        This command sends the upcoming event details within an embed message to the requester.
        :param ctx: the discord context of the message
        :param days: the number of days
        """
        try:
            if (type(days) != int or days <= 0):
                await ctx.reply("Please provide a valid number of days.")
                return

            results = await self._eventService.getEventsUpcoming(days)

            if (not results):
                await ctx.reply(f"There are no future events within {days} {'days' if days > 1 else 'day'}.")
                return

            embed = self.createEventEmbed(ctx=ctx, title="Upcoming Events", data=results, days=days, relative="startDate")
            
            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)
            await ctx.reply("Unable to get events.")

    def createEventEmbed(self, title:str, data:str, ctx:commands.context.Context=None, days: int = None, relative:str=None):
        embed = discord.embeds.Embed(title=title, color=discord.Colour.blurple())
        
        # Adding each event to field value
        eventInfo = ""
        for result in data:
            # Adding event title and dates
            if (result["endDate"]):
                eventInfo += f'**{result["name"]}**\n{result["startDate"]} to {result["endDate"]}\n'
            else:
                eventInfo += f'**{result["name"]}**\nStarting at {result["startDate"]}\n'

            # Adding the timer based on the parameter "relative", otherwise it checks for keys
            if (relative == "endDate"):
                eventInfo += f'End: {result["endDateRelative"]}\n\n'
            elif(relative == "startDate"):
                eventInfo += f'Start: {result["startDateRelative"]}\n\n'
            else:
                if ('endDateRelative' in result.keys()):
                    eventInfo += f'End: {result["endDateRelative"]}\n\n'
                else:
                    eventInfo += f'Start: {result["startDateRelative"]}\n\n'

        # Adjusting the field name based on days
        if (days):
            name=f"Within {days} {'days' if days > 1 else 'day'}:"
        else:
            name="Events:"

        embed.add_field(name=name, value=eventInfo)

        return embed
    
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

        if (eventsEnding or eventsComing):
            # Delete keywords if it exist so createEventEmbed works as intended
            for i in eventsEnding:
                i.pop("startDateRelative", None)
            for i in eventsComing:
                i.pop("endDateRelative", None)

            # Create embed of all event information
            embed = self.createEventEmbed(title="Princess Connect Daily Update", data = eventsEnding + eventsComing)

            # Print to every server if possible
            for guild in self._bot.guilds:
                try:
                    # Get to server channel if they have set server settings for it
                    guildCog: GuildCog = self._bot.get_cog('GuildCog')
                    if (guildCog):
                        result = await guildCog.getServerSettings(id=guild.id)
                        if (result and "notificationChannelID" in result.keys() and result["notificationChannelID"]):
                            # Print to notification channel based on settings
                            channel = self._bot.get_channel(result["notificationChannelID"])
                            if (channel):
                                if ("roleID" not in result.keys() or not result['roleID']):
                                    await channel.send(embed=embed)
                                    continue
                                else:
                                    roleName = f"<@&{result['roleID']}>"
                                    await channel.send(roleName, embed=embed)
                                    continue
                    
                    # Print to these channels if guild does not have guild settings or unable to get channel id
                    channel = discord.utils.get(guild.text_channels, name='priconne-notifications')
                    if (channel):
                        await channel.send(embed=embed)
                        continue

                    channel = discord.utils.get(guild.text_channels, name='princess-connect-notifications')
                    if (channel):
                        await channel.send(embed=embed)
                        continue
                except Exception as e:
                    print(e)
                    print(f"Something went wrong with sending a daily update to the server {guild}.")
    
    @princess_connect_daily_update.before_loop
    async def before_daily_update(self):
        """
        This method ensures the bot is fully setup before the daily update background task is done.
        """
        print("Waiting for bot to be ready before scraping data.")
        await self._bot.wait_until_ready()

async def setup(bot: DiscordBot):
    await bot.add_cog(InfoCog(bot=bot))