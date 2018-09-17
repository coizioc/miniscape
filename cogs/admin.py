"""Implements commands related to administrating a freemium-style text-based RPG."""
import asyncio
import datetime
import random

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

import config
from cogs.helper import channel_permissions as cp

class Admin():
    """Defines Admin commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @has_permissions(administrator=True)
    async def listchannels(self, ctx):
        """Lists the channels in which the bot is white/blacklisted."""
        guild_perms = cp.get_guild(ctx.guild.id)
        await ctx.send(guild_perms)

    @commands.command()
    @has_permissions(adminstrator=True)
    async def addblacklist(self, ctx):
        channel_mentions = ctx.message.channel_mentions

        if len(channel_mentions) > 0:
            out = ''
            for channel in channel_mentions:
                cp.add_channel(ctx.guild.id, channel, cp.BLACKLIST_KEY)
                out += f'{channel.name}, '
            await ctx.send(f"{out[:-2]} added to blacklist!")

    @commands.command()
    @has_permissions(adminstrator=True)
    async def addwhitelist(self, ctx):
        channel_mentions = ctx.message.channel_mentions

        if len(channel_mentions) > 0:
            out = ''
            for channel in channel_mentions:
                cp.add_channel(ctx.guild.id, channel, cp.WHITELIST_KEY)
                out += f'{channel.name}, '
            await ctx.send(f"{out[:-2]} added to whitelist!")

    @commands.command()
    @has_permissions(adminstrator=True)
    async def removeblacklist(self, ctx):
        channel_mentions = ctx.message.channel_mentions

        if len(channel_mentions) > 0:
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
    @has_permissions(adminstrator=True)
    async def removewhitelist(self, ctx):
        channel_mentions = ctx.message.channel_mentions

        if len(channel_mentions) > 0:
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


def setup(bot):
    """Adds the cog to the bot."""
    bot.add_cog(Admin(bot))
