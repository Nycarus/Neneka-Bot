import discord
from discord.ext import tasks, commands
from datetime import datetime, timedelta
import textwrap

from src.discord_bot import DiscordBot
from src.services.reminder_services import ReminderService
from src.models.reminder_model import ReminderModel
from src.utils.logger import setup_logger

class ReminderCog(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self._bot = bot
        self._reminderService = ReminderService()
        self.executeReminders.start()
        self._logger = setup_logger('bot.cog.reminder', '/data/discord.log')

    def cog_unload(self):
        self.executeReminders.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self._logger.info("reminder cog is ready.")

    @commands.hybrid_group(name="reminder", with_app_command=True, description="Make a reminder to yourself.", aliases=["remind, remindme, reminders"])
    async def reminder(self, ctx: commands.context.Context, days:int = commands.parameter(default=0, description="The number of days from now."), hours:int = commands.parameter(default=0, description="The number of hours from now."), minutes:int = commands.parameter(default=0, description="The number of minutes from now."), *, description= commands.parameter(default=None, description="The description of the reminder.")):
        """
        Add a new reminder.

        :param 
        """
        if (days <= 0 and hours <= 0 and minutes <= 0 or days < 0 or hours < 0 or minutes < 0):
            async with ctx.message.channel.typing():
                await ctx.reply("Please enter the proper amount of time to make the reminder.")
            return

        if (not description):
            async with ctx.message.channel.typing():
                await ctx.reply("Please enter the proper description for the reminder.")
            return

        try:
            description = "".join(description)
            date = datetime.utcnow() + timedelta(days=days, hours=hours, minutes=minutes)
            userID = ctx.author.id
            guildID = None
            channelID = None
            if (ctx.message.guild):
                guildID = ctx.message.guild.id
            if (ctx.message.channel):
                channelID = ctx.message.channel.id
            
            result = await self._reminderService.addReminder(date=date, description=description, userID=userID, guildID=guildID, channelID=channelID)

            if (result):
                epoch_time = datetime(1970, 1, 1)
                dateDifference = date - epoch_time

                embed = discord.embeds.Embed(title="Reminder", 
                    description=textwrap.dedent(
                    f"""
                    Hi, I will notify you in {days} {'days' if days > 1 else 'day'}, {hours} {'hours' if hours > 1 else 'hour'}, and {minutes} {'minutes' if minutes > 1 else 'minute'}.
                    Date: {f'<t:{int(dateDifference.total_seconds())}:f>'}
                    Time: {f'<t:{int(dateDifference.total_seconds())}:R>'}
                    
                    **With the message:**
                    {description}
                    """),
                    color=discord.Colour.blurple())

                embed.set_footer(text="Make sure the bot can DM you just in case.")

                async with ctx.message.channel.typing():
                    await ctx.reply(embed=embed)
            else:
                async with ctx.message.channel.typing():
                    await ctx.reply("I was not able to make the reminder.")
        except Exception as e:
            self._logger.error(e)

    @reminder.command(name="delete", with_app_command=True, description="Delete all reminders you have made.")
    async def reminderDelete(self, ctx: commands.context.Context):
        """
        Removes all your reminders.
        """
        result = await self._reminderService.deleteAllReminders(userID=ctx.author.id)
        if (result):
            async with ctx.message.channel.typing():
                await ctx.reply("Successfully deleted all of your reminders.")
        else:
            async with ctx.message.channel.typing():
                await ctx.reply("Unable to delete any of your reminders. You may not have any reminders.")

    @tasks.loop(minutes=1)
    async def executeReminders(self):
        try:
            reminders: list[ReminderModel] = await self._reminderService.getAndDeleteOldReminders()
        except Exception as ex:
            self._logger.error(ex)
            self._logger.error("Something was wrong with getting reminders.")
        
        # Send Reminders that are old
        if (reminders):
            for reminder in reminders:
                try:
                    # Creating message
                    epoch_time = datetime(1970, 1, 1)
                    currentDate = reminder.endDate - epoch_time
                    previousDate = reminder.startDate - epoch_time
                    embed = discord.embeds.Embed(title=f"Reminder from {f'<t:{int(previousDate.total_seconds())}:f>'}.", 
                        description=textwrap.dedent(
                        f"""
                        Hello, today is {f'<t:{int(currentDate.total_seconds())}:f>'} and I am here to notify you about your reminder.
                        
                        **Your message:**
                        {reminder.description}
                        """),
                        color=discord.Colour.blurple())

                    # attempt to print to guild channel, if bot still has access
                    if (reminder.guildID and reminder.channelID):
                        guild = self._bot.get_guild(reminder.guildID)
                        if (guild and guild.get_member(reminder.userID)): # check if user is still in the guild
                            channel = self._bot.get_channel(reminder.channelID)
                            if (channel): # check if channel still exist
                                async with channel.typing():
                                    await channel.send(f"<@{reminder.userID}>", embed=embed)
                                return
                    
                    # Print to user's DMs as backup if printing to channel fails
                    user = self._bot.get_user(reminder.userID)
                    await user.send(embed=embed)
                except Exception as e:
                    self._logger.error(e)
                    self._logger.error("Something went wrong with delivering reminder.")
        

    @executeReminders.before_loop
    async def before_daily_update(self):
        await self._bot.wait_until_ready()

async def setup(bot: DiscordBot):
    await bot.add_cog(ReminderCog(bot=bot))