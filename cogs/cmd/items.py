import string
from collections import Counter

from discord.ext import commands
from django.db.models import Q

import miniscape.command_helpers as ch
from cogs.cmd.common import get_display_name, has_post_permission
from cogs.helper import users
from config import MAX_PER_ACTION
from miniscape import item_helpers
from miniscape.models import User


class ItemCommands:

    @commands.command()
    async def bury(self, ctx, *args):
        """Buries items for prayer experience."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            number, name = ch.parse_number_and_name(args)
            if number and name:
                out = ch.bury(ctx.user_object, name, min(number, MAX_PER_ACTION))
                await ctx.send(out)

    @commands.command()
    async def food(self, ctx, search=''):
        """Show's the player's food in inventory."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            inventory = ch.print_food(ctx.user_object, search.lower())
            await self.paginate(ctx, inventory)

    @commands.command()
    async def value(self, ctx, search=''):
        """Show's the player's total inventory value."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            value = users.get_value_of_inventory(ctx.user_object)
            await self.paginate(ctx, inventory)

    @commands.group(aliases=['invent', 'inventory', 'item'], invoke_without_command=True)
    async def items(self, ctx, search=''):
        """Show's the player's inventory."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            inventory = ch.print_inventory(ctx.user_object, search.lower())
            await self.paginate(ctx, inventory)

    @items.command(name='info')
    async def _item_info(self, ctx, *args):
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            item = ' '.join(args)
            out = ch.print_item_stats(item)
            await ctx.send(out)

    @items.command(name='lock')
    async def _item_lock(self, ctx, *args):
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            item = ' '.join(args)
            if ctx.user_object.lock_item(item):
                out = f'{string.capwords(item)} has been locked!'
            else:
                out = (f'{string.capwords(item)} does not exist in your inventory. You must have it '
                       'present to lock it.')
            await ctx.send(out)

    @items.command(name='unlock')
    async def _item_unlock(self, ctx, *args):
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            item = ' '.join(args)
            if ctx.user_object.unlock_item(item):
                out = f'{string.capwords(item)} has been unlocked!'
            else:
                out = (f'{string.capwords(item)} does not exist in your inventory. You must have it '
                       'present to unlock it.')
            await ctx.send(out)

    @commands.command()
    async def claim(self, ctx, *args):
        """Claims xp/items from another item."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            number, name = ch.parse_number_and_name(args)
            out = ch.claim(ctx.user_object, name, number)
            await ctx.send(out)

    @commands.command()
    async def pull(self, ctx, *args):
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            number, name = ch.parse_number_and_name(args)
            other_person = User.objects.filter(Q(name__icontains=name) or Q(nick__icontains=name))[0]

            if other_person:
                out = ch.claim(ctx.user_object, "christmas cracker", number, other_person=other_person)
                await ctx.send(out)
            else:
                await ctx.send("You need to type the name of someone with whom you want to pull.")

    @commands.command(aliases=['starter'])
    async def starter_gear(self, ctx):
        """Gives the user a set of bronze armour."""
        author: User = ctx.user_object
        if has_post_permission(ctx.guild.id, ctx.channel.id):
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
    async def compare(self, ctx, item1, item2):
        """Compares the stats of two items."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            out = item_helpers.compare(item1.lower(), item2.lower())
            await ctx.send(out)

    @commands.group(invoke_without_command=True)
    async def shop(self, ctx):
        """Shows the items available at the shop."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            messages = item_helpers.print_shop(ctx.author.id)
            await self.paginate(ctx, messages)

    @commands.command()
    async def buy(self, ctx, *args):
        """Buys something from the shop."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            number, item = ch.parse_number_and_name(args)
            if number and item:
                out = item_helpers.buy(ctx.author.id, item, number=number)
                await ctx.send(out)

    @commands.command()
    async def sell(self, ctx, *args):
        """Sells the player's inventory for gold pieces."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            number, item = ch.parse_number_and_name(args)
            if number and item:
                out = item_helpers.sell(ctx.author.id, item, number=number)
                await ctx.send(out)

    #@commands.command()
    async def sellall(self, ctx, maxvalue=None):
        """Sells all items in the player's inventory (below a certain value) for gold pieces."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            name = get_display_name(ctx.author)
            if maxvalue is not None:
                value = users.get_value_of_inventory(ctx.author.id, under=maxvalue)
                users.update_inventory(ctx.author.id, value*["0"])
                users.clear_inventory(ctx.author.id, under=maxvalue)
                value_formatted = '{:,}'.format(value)
                maxvalue_formatted = '{:,}'.format(users.parse_int(maxvalue))
                name = get_display_name(ctx.author)
                out = f"All items in {name}'s inventory worth under {maxvalue_formatted} coins "\
                      f"sold for {value_formatted} coins!"
            else:
                value = users.get_value_of_inventory(ctx.author.id)
                users.update_inventory(ctx.author.id, value * ["0"])
                users.clear_inventory(ctx.author.id)
                value_formatted = '{:,}'.format(value)
                out = f"All items in {name}'s inventory "\
                      f"sold for {value_formatted} coins!"
            await ctx.send(out)
