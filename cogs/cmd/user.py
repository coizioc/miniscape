import string

from discord.ext import commands
from django.db.models import Q

from cogs.cmd.common import get_display_name, has_post_permission

from cogs.helper import items,  users
from cogs.errors.trade_error import TradeError
from miniscape.models import User, Item
from miniscape.itemconsts import FEDORA, COINS
import miniscape.command_helpers as ch
import miniscape.clue_helpers as clue_helpers
import miniscape.prayer_helpers as prayer
import miniscape.monster_helpers as mon
import miniscape.leaderboard_helpers as lb_helpers


class UserCommands:
    """UserCommands is a class that holds all commands related to users.
    This might be themselves (~me) or another user (~examine)"""

    @commands.group(invoke_without_command=True)
    async def me(self, ctx):
        """Shows information related to the user."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            await ctx.send(users.print_account(ctx.user_object))

    @me.group(name='stats', aliases=['levels'])
    async def _me_stats(self, ctx):
        """Shows the levels and stats of a user."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            await ctx.send(users.print_account(ctx.user_object, printequipment=False))

    @me.group(name='equipment', aliases=['armour', 'armor'])
    async def _me_equipment(self, ctx):
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            await ctx.send(users.print_equipment(ctx.user_object, with_header=True))

    @commands.command()
    async def kc(self, ctx, *args):
        await self._me_monsters(ctx, *args)

    @me.group(name='monsters')
    async def _me_monsters(self, ctx, *args):
        """Shows how many monsters a user has killed."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            out = mon.print_monster_kills(ctx.user_object, search=" ".join(args))
            await ctx.send(out)

    @me.command(name='clues')
    async def _me_clues(self, ctx):
        """Shows how many clue scrolls a user has completed."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            out = clue_helpers.print_clue_scrolls(ctx.user_object)
            await ctx.send(out)

    @me.command(name='pets')
    async def _me_pets(self, ctx):
        """Shows which pets a user has collected."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            messages = ch.print_pets(ctx.user_object)
            await self.paginate(ctx, messages)

    @commands.command(aliases=['lookup', 'finger', 'find'])
    async def examine(self, ctx, *args):
        """Examines a given user."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            search_string = ' '.join(args).lower()
            mems = await ctx.guild.query_members(query=search_string)
            for member in ctx.guild.members:
                if member.nick is not None:
                    if search_string in member.nick.lower():
                        target = User.objects.get(id=member.id)
                        break
                if search_string in member.name.lower():
                    target = User.objects.get(id=member.id)
                    break
            else:
                await ctx.send(f'Could not find {search_string} in server.')
                return

            await ctx.send(users.print_account(target))

    @commands.command()
    async def tolevel(self, ctx, *args):
        """Shows the user how much xp they need to get to a (specified) level."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            if args[0].isdigit():
                level = int(args[0])
                skill = ' '.join(args[1:])
            else:
                level = None
                skill = ' '.join(args)
            out = users.calc_xp_to_level(ctx.user_object, skill, level)
            await ctx.send(out)

    @commands.command()
    async def eat(self, ctx, *args):
        """Sets a food to eat during adventures."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            out = ch.eat(ctx.user_object, ' '.join(args).lower())
            await ctx.send(out)

    @commands.command()
    async def equip(self, ctx, *args):
        """Equips an item from a user's inventory."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            item = ' '.join(args)
            out = ch.equip_item(ctx.user_object, item.lower())
            await ctx.send(out)

    @commands.command()
    async def unequip(self, ctx, *args):
        """Unequips an item from a user's equipment."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            item = ' '.join(args)
            out = ch.unequip_item(ctx.user_object, item.lower())
            await ctx.send(out)


    @commands.command(aliases=['drank', 'chug', 'suckle'])
    async def drink(self, ctx, *args):
        """Drinks a potion."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            name = ' '.join(args)
            if ctx.user_object.drink(name):
                out = f'You drank the {name}! Your stats will be increased for your next adventure.'
            else:
                out = f'Unable to drink {name}'
            await ctx.send(out)


    @commands.command()
    async def tip(self, ctx, *args):
        """Posts a funny message if the user is wearing a certain item."""
        if has_post_permission(ctx.guild.id, ctx.channel.id) and ' '.join(args).lower() == 'fedora':
            user = User.objects.filter(Q(name__icontains=ctx.author.name) | Q(nick__icontains=ctx.author.name))
            if user:
                if user[0].equipment_slots[0] == FEDORA:
                    await ctx.send(f'*{ctx.author.name} tips their fedora.*')

    @commands.command(aliases=['pray', 'prayers'])
    async def prayer(self, ctx, *args):
        """Shows a list of available prayers, or sets a user's prayer."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            if not args:
                messages = prayer.print_list(ctx.author.id)
                await self.paginate(ctx, messages)
            else:
                if args[0] == 'info':
                    current_prayer = ' '.join(args[1:])
                    out = prayer.print_info(current_prayer)
                else:
                    out = prayer.set_prayer(ctx.author.id, ' '.join(args))
                await ctx.send(out)

    #@commands.command()
    async def trade(self, ctx, *args):
        """Trades to a person a number of a given object for a given price."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            if len(args) < 4:
                await ctx.send('Arguments missing. '
                               'Syntax is `~trade [name] [number] [item] [offer]`.')
                return

            try:
                trade = {'user1': ctx.author.id,
                         'user2': args[0],
                         'amount1': args[1],
                         'amount2': args[-1],
                         'item1': ' '.join(args[2:-1]),
                         'item2': 'coins'}
                ctx.bot.trade_manager.add_trade(ctx, trade)
            except TradeError as e:
                await ctx.send(e.msg)
                return

            name = args[0]
            for member in ctx.guild.members:
                if name.lower() in member.name.lower():
                    name_member = member
                    break

            offer = users.parse_int(args[-1])
            number = users.parse_int(args[1])
            itemid = items.find_by_name(' '.join(args[2:-1]))
            name = get_display_name(ctx.author)
            offer_formatted = '{:,}'.format(offer)
            out = (f'{items.SHOP_HEADER}{string.capwords(name)} wants to sell {name_member.mention} '
                   f'{items.add_plural(number, itemid)} for {offer_formatted} coins. '
                   f'To accept this offer, reply to this post with a :thumbsup:. '
                   f'Otherwise, this offer will expire in one minute.')
            msg = await ctx.send(out)

            if await self.confirm(ctx, msg, out, timeout=60):
                price = {"0": offer}
                users.update_inventory(name_member.id, price, remove=True)
                users.update_inventory(ctx.author.id, price)
                loot = {itemid: number}
                users.update_inventory(ctx.author.id, loot, remove=True)
                users.update_inventory(name_member.id, loot)

                buyer_name = get_display_name(name_member)
                await ctx.send(f'{items.SHOP_HEADER}{string.capwords(name)} successfully sold '
                               f'{items.add_plural(number, itemid)} to {buyer_name} for '
                               f'{offer_formatted} coins!')
            ctx.bot.trade_manager.reset_trade(trade, ctx.author.id, name_member.id)

    @commands.command(aliases=['ironmeme', 'btwman'])
    async def ironman(self, ctx):
        """Lets a user become an ironman, by the way."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            out = (':tools: __**IRONMAN**__ :tools:\n' \
                   'If you want to become an ironman, please react to this post with a :thumbsup:. '
                   'This will **RESET** your account and give you the ironman role. '
                   'You will be unable to trade with other players or gamble. '
                   'In return, you will be able to proudly display your status as an ironman, '
                   'by the way.')
            msg = await ctx.send(out)

            if await self.confirm(ctx, msg, out):
                ctx.user_object.reset_account()
                ctx.user_object.is_ironman = True
                ctx.user_object.save()
                # ironman_role = discord.utils.get(ctx.guild.roles, name="Ironman")
                # await ctx.author.add_roles(ironman_role, reason='Wanted to become an ironmeme.')
                name = get_display_name(ctx.author)
                await msg.edit(content=f':tools: __**IRONMAN**__ :tools:\n'
                                       f'Congratulations, {name}, you are now '
                                       'an ironman!')

    @commands.command(aliases=['imaloser', 'makemelame'])
    async def deironman(self, ctx):
        """Lets a user become an normal user."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            out = (':tools: __**IRONMAN**__ :tools:\n'
                   'If you want to remove your ironman status, please react to this post with a '
                   ':thumbsup:. This will keep your account the same as it is right now, but you '
                   'will be able to trade with others. If you want to re-ironman, you can type '
                   '`~ironman`, but you will have to reset your account.')
            msg = await ctx.send(out)

            if await self.confirm(ctx, msg, out):
                ctx.user_object.is_ironman = False
                ctx.user_object.save()
                # ironman_role = discord.utils.get(ctx.guild.roles, name="Ironman")
                # await ctx.author.remove_roles(
                #     ironman_role, reason="No longer wants to be ironmeme.")
                name = get_display_name(ctx.author)
                await msg.edit(
                    content=f':tools: __**IRONMAN**__ :tools:\n'
                            f'Congratulations, {name}, you are now a normal user!')

    @commands.command()
    async def balance(self, ctx, name=None):
        """Checks the user's balance."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            user: User = ctx.user_object
            item = Item.objects.get(name="coins")

            if name is None:
                amount = '{:,}'.format(user.get_item_by_item(COINS)[0].amount)
                name = get_display_name(ctx.author)
                await ctx.send(f'{name} has {amount} coins')
            elif name == 'universe':
                await ctx.send('As all things should be.')
            else:
                user = User.objects.filter(Q(name__icontains=name) | Q(nick__icontains=name))
                if not user:
                    await ctx.send(f'Name {name} not found in server.')
                elif len(user) > 1:
                    await ctx.send(f'Input {name} can refer to multiple people.')#({members})')
                else:
                    user = user[0]
                    amount = '{:,}'.format(user.get_item_by_item(COINS).amount)
                    await ctx.send(f'{user.plain_name} has {amount} coins')

    @commands.command(aliases=['leaderboards'])
    async def leaderboard(self, ctx, *args):
        """Allows users to easily compare each others' stats."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            name = " ".join(args) if args else None
            msg = await ctx.send("Select an emoji to load a leaderboard.")
            for emoji in lb_helpers.EMOJI.values():
                await msg.add_reaction(emoji)

            while True:
                reaction, user = await self.bot.wait_for('reaction_add')
                if user == ctx.author and reaction.message.id == msg.id:
                    for key in lb_helpers.EMOJI.keys():
                        if str(reaction.emoji) == lb_helpers.EMOJI[key]:
                            #await msg.edit(content=None)
                            await msg.edit(content=lb_helpers.get_leaderboard(key, name))

