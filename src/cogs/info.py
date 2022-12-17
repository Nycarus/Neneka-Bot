import discord
from discord.ext import tasks, commands
from src.discord_bot import DiscordBot
from src.utils.web_scraper import WebScraper
from src.services.event_service import EventService

class InfoCog(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self._bot = bot
        self.princess_connect_daily_update.start()
        self._eventService = EventService()

    def cog_unload(self):
        self.princess_connect_daily_update.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print("info cog is ready.")

    @commands.command(name="current")
    async def events_current(self, ctx, member:discord.Member=None):
        try:
            results = await self._eventService.getCurrentEvents()

            if (not results):
                await ctx.send("There are no current events.")

            embed = discord.embeds.Embed(title="Current Events", color=discord.Colour.blurple())
            for result in results:
                embed.add_field(name=f'{result["name"]}', value=f'{result["startDate"]} to {result["endDate"]}', inline= True)
            if (member):
                embed.set_footer(text=f'{member.display_name} asked for current events.')
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            await ctx.send("Unable to get events.")
    
    @commands.command(name="ending")
    async def events_ending(self, ctx, days:int, member:discord.Member=None):
        try:
            if (not days):
                await ctx.send("Please provide a valid argument for the amount of days.")

            results = await self._eventService.getEventsEnding(days)

            if (not results):
                await ctx.send(f"There are no events ending with {days} days.")

            embed = discord.embeds.Embed(title="Events Ending", color=discord.Colour.blurple())
            for result in results:
                if (result["endDate"]):
                    embed.add_field(name=f'{result["name"]}', value=f'{result["startDate"]} to {result["endDate"]}\nEnding {result["endDateRelative"]}')
                else:
                    embed.add_field(name=f'{result["name"]}', value=f'Starting at {result["startDate"]}\n')
            if (member):
                embed.set_footer(text=f'{member.display_name} asked for current events.')
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            await ctx.send("Unable to get events.")
    
    @commands.command(name="upcoming")
    async def events_upcoming(self, ctx, days:int, member:discord.Member=None):
        try:
            if (not days):
                await ctx.send("Please provide a valid argument for the amount of days.")

            results = await self._eventService.getEventsUpcoming(days)

            if (not results):
                await ctx.send(f"There are no future events with {days} days.")

            embed = discord.embeds.Embed(title="Upcoming Events", color=discord.Colour.blurple())
            for result in results:
                if (result["endDate"]):
                    embed.add_field(name=f'{result["name"]}', value=f'{result["startDate"]} to {result["endDate"]}\nStarting {result["startDateRelative"]}')
                else:
                    embed.add_field(name=f'{result["name"]}', value=f'Starting at {result["startDate"]}\nStarting {result["startDateRelative"]}')
            if (member):
                embed.set_footer(text=f'{member.display_name} asked for current events.')
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            await ctx.send("Unable to get events.")

    @tasks.loop(hours=24.0)
    async def princess_connect_daily_update(self):
        print("Updating daily info.")

        print("Deleting expired events.")
        await self._eventService.cleanExpiredEvents()

        print("Webscraping crunchyroll princess connect news website.")
        events = await WebScraper.scrape_crunchyroll_events()
        if (events):
            print ("Adding events to database.")
            await self._eventService.addEvents(events)

    @princess_connect_daily_update.before_loop
    async def before_daily_update(self):
        print("pre-update")

async def setup(bot: DiscordBot):
    await bot.add_cog(InfoCog(bot=bot))