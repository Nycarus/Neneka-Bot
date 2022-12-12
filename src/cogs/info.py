from discord.ext import tasks, commands
from src.discord_bot import DiscordBot

class InfoCog(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self.bot = bot
        self.princess_connect_daily_update.start()
    
    def cog_unload(self):
        self.princess_connect_daily_update.cancel()

    @tasks.loop(hours=24.0)
    async def princess_connect_daily_update(self):
        print("Updating daily info")

    @princess_connect_daily_update.before_loop
    async def before_daily_update(self):
        print("pre-update")

async def setup(bot: DiscordBot):
    await bot.add_cog(InfoCog(bot=bot))