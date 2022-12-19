import discord
from discord.ext import tasks, commands
from src.discord_bot import DiscordBot
from src.services.guild_service import GuildService

class GuildCog(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self._bot = bot
        self._guildServices = GuildService()

    def cog_unload(self):
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        print("guild cog is ready.")
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.guild.Guild):
        try:
            await self._guildServices.addGuild(guild.id)

            # Send help embed to the owner's dms.
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
        if (not ctx.message.guild):
            await ctx.send("This command can only be used in a server.")
            return

        # prevent people from using this command if they are not owner or admin
        if (not (ctx.author.guild_permissions.administrator or ctx.author == ctx.guild.owner)):
            await ctx.send("You do not have permission to use this command.")
            return

        if (not (notificationChannel or commandChannel)):
            await ctx.send("Please provide a notification or command channel.")
            return
        
        # Attempt to update guild information
        try:
            notificationChannelID = None
            commandChannelID = None
            if (notificationChannel):
                notificationChannelID = notificationChannel.id
            if(commandChannel):
                commandChannelID = commandChannel.id

            result = await self._guildServices.updateGuild(id=ctx.message.guild.id, notificationChannelID=notificationChannelID, commandChannelID=commandChannelID)

            if (result):
                await ctx.send("Server has successfully updated settings.")
            else:
                await ctx.send("Unable to update server settings.")
            
        except Exception as e:
            print(e)
            await ctx.send("Guild setup has failed unexpectedly. Make sure the bot has access to those channels and they are spelled correctly.")

async def setup(bot: DiscordBot):
    await bot.add_cog(GuildCog(bot=bot))