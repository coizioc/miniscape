import string
from collections import Counter

from discord.ext import commands
from django.db.models import Q

import miniscape.command_helpers as ch
import utils.command_helpers
from cogs.cmd.checks import can_post
from config import MAX_PER_ACTION
from miniscape import item_helpers
from miniscape.models import User


class ItemCommands:

    @commands.command()
    @can_post()
    async def bury(self, ctx, *args):
        """Buries items for prayer experience."""
        number, name = utils.command_helpers.parse_number_and_name(args)
        if number and name:
            out = ch.bury(ctx.user_object, name, min(number, MAX_PER_ACTION))
            await ctx.send(out)

    @commands.command()
    @can_post()
    async def food(self, ctx, search=''):
        """Show's the player's food in inventory."""
        inventory = ch.print_food(ctx.user_object, search.lower())
        await self.paginate(ctx, inventory)

    @commands.command()
    @can_post()
    async def value(self, ctx, search=''):
        """Show's the player's total inventory value."""
        inventory = ch.print_value(ctx.user_object, search.lower())
        await self.paginate(ctx, inventory)

    @commands.group(aliases=['invent', 'inventory', 'item'], invoke_without_command=True)
    @can_post()
    async def items(self, ctx, search=''):
        """Show's the player's inventory."""
        inventory = ch.print_inventory(ctx.user_object, search.lower())
        await self.paginate(ctx, inventory)

    @items.command(name='info')
    @can_post()
    async def _item_info(self, ctx, *args):
        item = ' '.join(args)
        out = ch.print_item_stats(item)
        await ctx.send(out)

    @items.command(name='lock')
    @can_post()
    async def _item_lock(self, ctx, *args):
        item = ' '.join(args)
        if ctx.user_object.lock_item(item):
            out = f'{string.capwords(item)} has been locked!'
        else:
            out = (f'{string.capwords(item)} does not exist in your inventory. You must have it '
                   'present to lock it.')
        await ctx.send(out)

    @items.command(name='unlock')
    @can_post()
    async def _item_unlock(self, ctx, *args):
        item = ' '.join(args)
        if ctx.user_object.unlock_item(item):
            out = f'{string.capwords(item)} has been unlocked!'
        else:
            out = (f'{string.capwords(item)} does not exist in your inventory. You must have it '
                   'present to unlock it.')
        await ctx.send(out)

    @commands.command()
    @can_post()
    async def claim(self, ctx, *args):
        """Claims xp/items from another item."""
        number, name = utils.command_helpers.parse_number_and_name(args)
        out = ch.claim(ctx.user_object, name, number)
        await ctx.send(out)

    @commands.command()
    @can_post()
    async def pull(self, ctx, *args):
        number, name = utils.command_helpers.parse_number_and_name(args)
        other_person = User.objects.filter(Q(name__icontains=name) or Q(nick__icontains=name))[0]

        if other_person:
            out = ch.claim(ctx.user_object, "christmas cracker", number, other_person=other_person)
            await ctx.send(out)
        else:
            await ctx.send("You need to type the name of someone with whom you want to pull.")

    @commands.command(aliases=['starter'])
    @can_post()
    async def starter_gear(self, ctx):
        """Gives the user a set of bronze armour."""
        author: User = ctx.user_object
        if author.combat_xp == 0:
            author.update_inventory(Counter([63, 66, 69, 70, 64, 72]))

            await ctx.send(f'Bronze set given to {author.plain_name}! You can see your items '
                           f'by typing `~inventory` in #bank and equip them by typing `~equip '
                           f'[item]`. You can see your current stats by typing `~me`. '
                           f'If you need help with commands, feel free to look at #welcome '
                           f'or ask around!')
        else:
            await ctx.send(
                f'You are too experienced to get the starter gear, {ctx.author.name}.')

    @commands.command()
    @can_post()
    async def compare(self, ctx, item1, item2):
        """Compares the stats of two items."""
        out = item_helpers.compare(item1.lower(), item2.lower())
        await ctx.send(out)

    @commands.group(invoke_without_command=True)
    @can_post()
    async def shop(self, ctx):
        """Shows the items available at the shop."""
        messages = item_helpers.print_shop(ctx.author.id)
        await self.paginate(ctx, messages)

    @commands.command()
    @can_post()
    async def buy(self, ctx, *args):
        """Buys something from the shop."""
        number, item = utils.command_helpers.parse_number_and_name(args)
        if number and item:
            out = item_helpers.buy(ctx.author.id, item, number=number)
            await ctx.send(out)

    @commands.command()
    @can_post()
    async def sell(self, ctx, *args):
        """Sells the player's inventory for gold pieces."""
        number, item = utils.command_helpers.parse_number_and_name(args)
        if number and item:
            out = item_helpers.sell(ctx.author.id, item, number=number)
            await ctx.send(out)
