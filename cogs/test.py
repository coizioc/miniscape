"""Implements commands used for testing/debugging new miniscape content."""
import discord
from discord.ext import commands
from django.db.models import Q

from miniscape import command_helpers as ch
from miniscape.models import User, Item


class Test():
    """Defines Test commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def giveself(self, ctx, *args):
        """Gives the user a number of an item"""
        number, name = ch.parse_number_and_name(args)
        item = Item.objects.filter(name__icontains=name)
        if not item:
            await ctx.send(f'{name} not found.')
        else:
            ctx.user_object.update_inventory(item[0], number)
            await ctx.send(f"{number} {name} given!")

    @commands.command()
    async def cleardailies(self, ctx):
        """Resets the progress of dailies for the user."""
        ctx.user_object.clear_dailies()
        await ctx.send("Dailies progress reset!")


def setup(bot):
    """Adds the cog to the bot."""
    bot.add_cog(Test(bot))
