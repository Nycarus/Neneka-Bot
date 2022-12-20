import discord
from discord.ext import commands
from src.discord_bot import DiscordBot
from src.services.guild_service import GuildService
import textwrap

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
            value=textwrap.dedent(
            f"""
            - Use the command `;setup #notification-channel @notification-role` to choose channels where this bot will send messages to.
            - Alternatively, you may choose to create a `#princess-connect-notification` or `#priconne-notification` channel to receive notifications.

            - Use `;help` to see a list of commands.
            """))
            await guild.owner.send(embed=embed)
        except Exception as e:
            print(e)
            print(f'{guild.owner} has their dms turned off')

    @commands.hybrid_command(name="setup", pass_context=True)
    async def setup(self, ctx: commands.context.Context, notificationChannel:discord.TextChannel = None, role:discord.Role = None):
        if (not ctx.message.guild):
            await ctx.reply("This command can only be used in a server.")
            return

        # prevent people from using this command if they are not owner or admin
        if (not (ctx.author.guild_permissions.administrator or ctx.author == ctx.guild.owner)):
            await ctx.reply("You do not have permission to use this command.")

        # check if channels are the proper type
        if (notificationChannel and type(notificationChannel) != discord.TextChannel):
            await ctx.reply("Please enter a proper notification channel. You can do this with #channel.")
            return

        # check if roles are the proper type
        if (role and type(role) != discord.Role):
            await ctx.reply("Please enter a proper role.")
            return
    
        # Attempt to update guild information
        try:
            notificationChannelID = None
            roleID = None
            if (notificationChannel):
                notificationChannelID = notificationChannel.id
            if (role):
                roleID = role.id

            result = await self._guildServices.updateGuild(id=ctx.message.guild.id, notificationChannelID=notificationChannelID, roleID=roleID)

            if (result):
                await ctx.reply("Server has successfully updated settings.")
            else:
                await ctx.reply("Unable to update server settings.")
            
        except Exception as e:
            print(e)
            await ctx.reply("Guild setup has failed unexpectedly. Make sure the bot has access to those channels and they are spelled correctly.")

    async def getServerSettings(self, id: int):
        return await self._guildServices.getServerSettings(id=id)

async def setup(bot: DiscordBot):
    await bot.add_cog(GuildCog(bot=bot))