import discord
from discord.ext import commands
from django.db.models import Q

from cogs.cmd.checks import can_post
from cogs.cmd.common import get_display_name

from mbot import MiniscapeBotContext
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
    @can_post()
    async def me(self, ctx: MiniscapeBotContext):
        """Shows information related to the user."""
        await ctx.send(ctx.user_object.print_account())

    @me.group(name='stats', aliases=['levels'])
    @can_post()
    async def _me_stats(self, ctx: MiniscapeBotContext):
        """Shows the levels and stats of a user."""
        await ctx.send(ctx.user_object.print_account(print_equipment=False))

    @me.group(name='equipment', aliases=['armour', 'armor'])
    @can_post()
    async def _me_equipment(self, ctx: MiniscapeBotContext):
        await ctx.send(ctx.user_object.print_equipment(with_header=True))

    @commands.command()
    @can_post()
    async def kc(self, ctx: MiniscapeBotContext, *args):
        await self._me_monsters(ctx, *args)

    @me.group(name='monsters')
    @can_post()
    async def _me_monsters(self, ctx: MiniscapeBotContext, *args):
        """Shows how many monsters a user has killed."""
        out = mon.print_monster_kills(ctx.user_object, search=" ".join(args))
        await ctx.send(out)

    @me.command(name='clues')
    @can_post()
    async def _me_clues(self, ctx: MiniscapeBotContext):
        """Shows how many clue scrolls a user has completed."""
        out = clue_helpers.print_clue_scrolls(ctx.user_object)
        await ctx.send(out)

    @me.command(name='pets')
    @can_post()
    async def _me_pets(self, ctx: MiniscapeBotContext):
        """Shows which pets a user has collected."""
        messages = ch.print_pets(ctx.user_object)
        await self.paginate(ctx, messages)

    @commands.command(aliases=['lookup', 'finger', 'find'])
    @can_post()
    async def examine(self, ctx: MiniscapeBotContext, *args):
        """Examines a given user."""
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

        await ctx.send(target.print_account())

    @commands.command()
    @can_post()
    async def tolevel(self, ctx: MiniscapeBotContext, *args):
        """Shows the user how much xp they need to get to a (specified) level."""
        if args[0].isdigit():  # ~tolevel 99 artisan
            level = int(args[0])
            skill = ' '.join(args[1:])
        else:  # ~tolevel artisan (e.g. next level)
            skill = ' '.join(args)
            try:
                level = ctx.user_object.skill_level_mapping[skill] + 1
            except KeyError:
                out = f'{skill} is not a skill.'
                await ctx.reply(mention_author=False, embed=discord.Embed(type="rich", description=out, title=""))
                return

        result = ctx.user_object.calc_xp_to_level(skill, level)
        try:  # It succeeded and we got an integer back
            result_int = int(result)
            if result_int < 1:
                out = f"You are already level {level} in {skill}!"
            else:
                xp_formatted = '{:,}'.format(result)
                out = f'You need {xp_formatted} xp to get level {level} in {skill}.'
        except ValueError:  # We got an error message back
            out = result

        await ctx.reply(mention_author=False, embed=discord.Embed(type="rich", description=out, title=""))

    @commands.command()
    @can_post()
    async def eat(self, ctx: MiniscapeBotContext, *args):
        """Sets a food to eat during adventures."""
        out = ch.eat(ctx.user_object, ' '.join(args).lower())
        await ctx.send(out)

    @commands.command()
    @can_post()
    async def equip(self, ctx: MiniscapeBotContext, *args):
        """Equips an item from a user's inventory."""
        item = ' '.join(args)
        out = ch.equip_item(ctx.user_object, item.lower())
        await ctx.send(out)

    @commands.command()
    @can_post()
    async def unequip(self, ctx: MiniscapeBotContext, *args):
        """Unequips an item from a user's equipment."""
        item = ' '.join(args)
        out = ch.unequip_item(ctx.user_object, item.lower())
        await ctx.send(out)

    @commands.command(aliases=['drank', 'chug', 'suckle'])
    @can_post()
    async def drink(self, ctx: MiniscapeBotContext, *args):
        """Drinks a potion."""
        name = ' '.join(args)
        if ctx.user_object.drink(name):
            out = f'You drank the {name}! Your stats will be increased for your next adventure.'
        else:
            out = f'Unable to drink {name}'
        await ctx.send(out)

    @commands.command()
    @can_post()
    async def tip(self, ctx: MiniscapeBotContext, *args):
        """Posts a funny message if the user is wearing a certain item."""
        if ' '.join(args).lower() == 'fedora':
            user = User.objects.filter(Q(name__icontains=ctx.author.name) | Q(nick__icontains=ctx.author.name))
            if user:
                if user[0].equipment_slots[0] == FEDORA:
                    await ctx.send(f'*{ctx.author.name} tips their fedora.*')

    @commands.command(aliases=['pray', 'prayers'])
    @can_post()
    async def prayer(self, ctx: MiniscapeBotContext, *args):
        """Shows a list of available prayers, or sets a user's prayer."""
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

    # TODO(mitch): reenable trading?
    # @commands.command()
    # @can_post()
    # async def trade(self, ctx, *args):
    #     """Trades to a person a number of a given object for a given price."""
    #         if len(args) < 4:
    #             await ctx.send('Arguments missing. '
    #                            'Syntax is `~trade [name] [number] [item] [offer]`.')
    #             return
    #
    #         try:
    #             trade = {'user1': ctx.author.id,
    #                      'user2': args[0],
    #                      'amount1': args[1],
    #                      'amount2': args[-1],
    #                      'item1': ' '.join(args[2:-1]),
    #                      'item2': 'coins'}
    #             ctx.bot.trade_manager.add_trade(ctx, trade)
    #         except TradeError as e:
    #             await ctx.send(e.msg)
    #             return
    #
    #         name = args[0]
    #         for member in ctx.guild.members:
    #             if name.lower() in member.name.lower():
    #                 name_member = member
    #                 break
    #
    #         offer = users.parse_int(args[-1])
    #         number = users.parse_int(args[1])
    #         itemid = items.find_by_name(' '.join(args[2:-1]))
    #         name = get_display_name(ctx.author)
    #         offer_formatted = '{:,}'.format(offer)
    #         # out = (f'{items.SHOP_HEADER}{string.capwords(name)} wants to sell {name_member.mention} '
    #         #        f'{items.add_plural(number, itemid)} for {offer_formatted} coins. '
    #         #        f'To accept this offer, reply to this post with a :thumbsup:. '
    #         #        f'Otherwise, this offer will expire in one minute.')
    #         msg = await ctx.send(out)
    #
    #         if await self.confirm(ctx, msg, out, timeout=60):
    #             price = {"0": offer}
    #             users.update_inventory(name_member.id, price, remove=True)
    #             users.update_inventory(ctx.author.id, price)
    #             loot = {itemid: number}
    #             users.update_inventory(ctx.author.id, loot, remove=True)
    #             users.update_inventory(name_member.id, loot)
    #
    #             buyer_name = get_display_name(name_member)
    #             # await ctx.send(f'{items.SHOP_HEADER}{string.capwords(name)} successfully sold '
    #             #                f'{items.add_plural(number, itemid)} to {buyer_name} for '
    #             #                f'{offer_formatted} coins!')
    #         ctx.bot.trade_manager.reset_trade(trade, ctx.author.id, name_member.id)

    @commands.command(aliases=['ironmeme', 'btwman'])
    @can_post()
    async def ironman(self, ctx: MiniscapeBotContext):
        """Lets a user become an ironman, by the way."""
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
    @can_post()
    async def deironman(self, ctx: MiniscapeBotContext):
        """Lets a user become an normal user."""
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
    @can_post()
    async def balance(self, ctx: MiniscapeBotContext, name=None):
        """Checks the user's balance."""
        user: User = ctx.user_object

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
                await ctx.send(f'Input {name} can refer to multiple people.')  # ({members})')
            else:
                user = user[0]
                amount = '{:,}'.format(user.get_item_by_item(COINS).amount)
                await ctx.send(f'{user.plain_name} has {amount} coins')

    @commands.command(aliases=['leaderboards'])
    @can_post()
    async def leaderboard(self, ctx: MiniscapeBotContext, *args):
        """Allows users to easily compare each others' stats."""
        name = " ".join(args) if args else None
        msg = await ctx.send("Select an emoji to load a leaderboard.")
        for emoji in lb_helpers.EMOJI.values():
            await msg.add_reaction(emoji)

        while True:
            reaction, user = await self.bot.wait_for('reaction_add')
            if user == ctx.author and reaction.message.id == msg.id:
                for key in lb_helpers.EMOJI.keys():
                    if str(reaction.emoji) == lb_helpers.EMOJI[key]:
                        # await msg.edit(content=None)
                        await msg.edit(content=lb_helpers.get_leaderboard(key, name))
