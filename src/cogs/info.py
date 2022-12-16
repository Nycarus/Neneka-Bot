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