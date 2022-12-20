import discord
from discord.ext import tasks, commands
from src.discord_bot import DiscordBot
from src.services.reminder_services import ReminderService
from datetime import datetime, timedelta
from src.models.reminder_model import ReminderModel
import asyncio

class ReminderCog(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self._bot = bot
        self._reminderService = ReminderService()
        self.executeReminders.start()

    def cog_unload(self):
        self.executeReminders.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print("reminder cog is ready.")

    @commands.hybrid_command(name="reminder", with_app_command=True, description="Make a reminder to yourself.", aliases=["remind, remindme, reminders"])
    async def reminder(self, ctx: commands.context.Context, days:int, hours:int, minutes:int, *, description=None):
        if (days <= 0 and hours <= 0 and minutes <= 0 or days < 0 or hours < 0 or minutes < 0):
            await ctx.reply("Please enter the proper amount of time to make the reminder.")

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
                    description=
                    f"""
                    I will notify you in {days} {'days' if days > 1 else 'day'}, {hours} {'hours' if hours > 1 else 'hour'}, and {minutes} {'minutes' if minutes > 1 else 'minute'}.
                    Date: {f'<t:{int(dateDifference.total_seconds())}:f>'}
                    Time: {f'<t:{int(dateDifference.total_seconds())}:R>'}
                    
                    **With the message:**
                    {description}
                    """,
                    color=discord.Colour.blurple())

                embed.set_footer(text="Make sure the bot can DM you just in case.")

                await ctx.reply(embed=embed)
            else:
                await ctx.reply("I was not able to make the reminder.")
        except Exception as e:
            print(e)

    @tasks.loop(minutes=1)
    async def executeReminders(self):
        try:
            # Check for reminders
            reminders: list[ReminderModel] = await self._reminderService.getAndDeleteOldReminders()
        except Exception as ex:
            print(ex)
            print("Something was wrong with getting reminders.")
        
        # Send Reminders that are old
        if (reminders):
            print("sending reminders")
            
            for reminder in reminders:
                try:
                    # Creating message
                    epoch_time = datetime(1970, 1, 1)
                    currentDate = reminder.endDate - epoch_time
                    previousDate = reminder.startDate - epoch_time
                    embed = discord.embeds.Embed(title=f"Reminder from {f'<t:{int(previousDate.total_seconds())}:f>'}.", 
                        description=
                        f"""
                        Hello, today is {f'<t:{int(currentDate.total_seconds())}:f>'} and I am here to notify you about your reminder.
                        
                        **Your message:**
                        {reminder.description}
                        """,
                        color=discord.Colour.blurple())

                    # attempt to print to guild channel, if bot still has access
                    if (reminder.guildID and reminder.channelID):
                        guild = self._bot.get_guild(reminder.guildID)
                        if (guild and guild.get_member(reminder.userID)): # check if user is still in the guild
                            channel = self._bot.get_channel(reminder.channelID)
                            if (channel): # check if channel still exist
                                await channel.send(f"<@{reminder.userID}>", embed=embed)
                                return
                    
                    # Print to user's DMs as backup if printing to channel fails
                    user = self._bot.get_user(reminder.userID)
                    await user.send(embed=embed)
                except Exception as e:
                    print(e)
                    print("Something went wrong with delivering reminder.")
        

    @executeReminders.before_loop
    async def before_daily_update(self):
        await self._bot.wait_until_ready()

async def setup(bot: DiscordBot):
    await bot.add_cog(ReminderCog(bot=bot))