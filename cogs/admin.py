"""Implements commands related to administrating a freemium-style text-based RPG."""
from discord.ext import commands
from discord.ext.commands import has_permissions
from cogs.cmd import channel_permissions as cp


class Admin(commands.Cog):
    """Defines Admin commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @has_permissions(manage_guild=True)
    async def listchannels(self, ctx):
        """Lists the channels in which the bot is white/blacklisted."""
        guild_perms = cp.get_guild(ctx.guild.id)
        await ctx.send(guild_perms)

    @commands.command()
    @has_permissions(manage_guild=True)
    async def addblacklist(self, ctx):
        """Adds a guild to the blacklist."""
        channel_mentions = ctx.message.channel_mentions

        if channel_mentions:
            out = ''
            for channel in channel_mentions:
                cp.add_channel(ctx.guild.id, channel.id, cp.BLACKLIST_KEY)
                out += f'{channel.name}, '
            await ctx.send(f"{out[:-2]} added to blacklist!")

    @commands.command()
    @has_permissions(manage_guild=True)
    async def addwhitelist(self, ctx):
        """Adds a guild to the whitelist."""
        channel_mentions = ctx.message.channel_mentions

        if channel_mentions:
            out = ''
            for channel in channel_mentions:
                cp.add_channel(ctx.guild.id, channel.id, cp.WHITELIST_KEY)
                out += f'{channel.name}, '
            await ctx.send(f"{out[:-2]} added to whitelist!")

    @commands.command(aliases=['removeac'])
    @has_permissions(manage_guild=True)
    async def removeannoucement(self, ctx):
        """Removes an announcements channel."""
        cp.clear_channel(ctx.guild.id, cp.ANNOUNCEMENT_KEY)
        await ctx.send(f"Removed annoucements channel!")

    @commands.command()
    @has_permissions(manage_guild=True)
    async def removeblacklist(self, ctx):
        """Removes a blacklisted channel."""
        channel_mentions = ctx.message.channel_mentions

        if channel_mentions:
            out = ''
            for channel in channel_mentions:
                try:
                    cp.remove_channel(ctx.guild.id, channel.id, cp.BLACKLIST_KEY)
                    out += f'{channel.name}, '
                except ValueError:
                    pass
            if len(out) < 2:
                out = 'No channels were  '
            await ctx.send(f"{out[:-2]} removed from blacklist!")

    @commands.command()
    @has_permissions(manage_guild=True)
    async def removewhitelist(self, ctx):
        """Removes a whitelisted guild."""
        channel_mentions = ctx.message.channel_mentions

        if channel_mentions:
            out = ''
            for channel in channel_mentions:
                try:
                    cp.remove_channel(ctx.guild.id, channel.id, cp.WHITELIST_KEY)
                    out += f'{channel.name}, '
                except ValueError:
                    pass
            if len(out) < 2:
                out = 'No channels were  '
            await ctx.send(f"{out[:-2]} removed from whitelist!")

    @commands.command(aliases=['setac'])
    @has_permissions(manage_guild=True)
    async def setannouncement(self, ctx):
        """Sets the default announcements channel."""
        channel_mentions = ctx.message.channel_mentions

        if channel_mentions:
            announcement_channel = channel_mentions[0]
            cp.set_channel(ctx.guild.id, announcement_channel.id, cp.ANNOUNCEMENT_KEY)
            await ctx.send(f"{announcement_channel.name} set as announcements channel!")

def setup(bot):
    """Adds the cog to the bot."""
    bot.add_cog(Admin(bot))
