"""Implements commands related to running a freemium-style text-based RPG."""
import asyncio
import datetime
import random
from collections import Counter
import traceback
import logging
import sys

import discord
from discord.ext import commands
from django.db.models import Q

from config import ARROW_LEFT_EMOJI, ARROW_RIGHT_EMOJI, THUMBS_UP_EMOJI, TICK_SECONDS
from cogs.helper import channel_permissions as cp
from cogs.helper import clues
from miniscape import adventures as adv, item_helpers, craft_helpers
from cogs.helper import craft
from cogs.helper import items
from cogs.helper import quests
from cogs.helper import slayer
from cogs.helper import users
from cogs.helper import vis
from cogs.errors.trade_error import TradeError
from miniscape.models import User, Item
import miniscape.command_helpers as ch
import miniscape.slayer_helpers as sh
import miniscape.clue_helpers as clue_helpers
import miniscape.prayer_helpers as prayer
import miniscape.monster_helpers as mon
import miniscape.quest_helpers as quest_helpers


MAX_PER_ACTION = 10000
REAPER_TOKEN = Item.objects.get(name__iexact="reaper token")


class AmbiguousInputError(Exception):
    """Error raised for input that refers to multiple users"""
    def __init__(self, output):
        self.output = output


def get_member_from_guild(guild_members, username):
    """From a str username and a list of all guild members returns the member whose name contains username."""
    username = username.lower()
    if username == 'rand':
        return random.choice(guild_members)
    else:
        members = []
        for member in guild_members:
            if member.nick is not None:
                if username == member.nick.replace(' ', '').lower():
                    return member
                elif username in member.nick.replace(' ', '').lower():
                    members.append(member)
            elif username == member.name.replace(' ', '').lower():
                return member
            elif username in member.name.replace(' ', '').lower():
                members.append(member)

        members_len = len(members)
        if members_len == 0:
            raise NameError(username)
        elif members_len == 1:
            return members[0]
        else:
            raise AmbiguousInputError([member.name for member in members])


def get_display_name(member):
    """Gets the displayed name of a user."""
    if member.nick is None:
        name = member.name
    else:
        name = member.nick
    if User.objects.get(id=member.id).is_ironman:
        name += ' (IM)'
    return name


def parse_name(guild, username):
    """Gets the username of a user from a string and guild."""
    if '@' in username:
        try:
            return guild.get_member(int(username[3:-1]))
        except:
            raise NameError(username)
    else:
        return get_member_from_guild(guild.members, username)


def has_post_permission(guildid, channelid):
    """Checks whether the bot can post in that channel."""
    # if cp.in_panic():
    #     return channelid == TEST_CHANNEL

    guild_perms = cp.get_guild(guildid)
    try:
        for blacklist_channel in guild_perms[cp.BLACKLIST_KEY]:
            if channelid == blacklist_channel:
                return False
    except KeyError:
        pass

    if cp.WHITELIST_KEY in guild_perms.keys():
        if len(guild_perms[cp.WHITELIST_KEY]) > 0:
            try:
                for whitelist_channel in guild_perms[cp.WHITELIST_KEY]:
                    if channelid == whitelist_channel:
                        break
                else:
                    return False
            except KeyError:
                pass
    return True


class Miniscape():
    """Defines Miniscape commands."""

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.check_adventures())
        self.bot.loop.create_task(self.reset_dailies())


    # @commands.command()
    # async def commands(self, ctx):
    #     """Sends the user a message listing the bot's commands."""
    #     with open(HELP_FILE, 'r') as f:
    #         message = f.read().splitlines()
    #     await ctx.send_message(ctx.author, message)

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
            for member in ctx.guild.members:
                if member.nick is not None:
                    if search_string in member.nick.lower():
                        name = member.nick
                        break
                if search_string in member.name.lower():
                    name = member.name
                    break
            else:
                await ctx.send(f'Could not find {search_string} in server.')
                return

            target = User.objects.get(id=member.id)
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

    @commands.command()
    async def bury(self, ctx, *args):
        """Buries items for prayer experience."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            try:
                number = users.parse_int(args[0])
                if number >= MAX_PER_ACTION:
                    number = MAX_PER_ACTION
                item = ' '.join(args[1:])
            except ValueError:
                number = 1
                item = ' '.join(args)
            out = ch.bury(ctx.user_object, item, number)
            await ctx.send(out)

    @commands.command(aliases=['pray', 'prayers'])
    async def prayer(self, ctx, *args):
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            if len(args) == 0:
                messages = prayer.print_list(ctx.author.id)
                await self.paginate(ctx, messages)
            else:
                if args[0] == 'info':
                    current_prayer = ' '.join(args[1:])
                    out = prayer.print_info(current_prayer)
                else:
                    out = prayer.set_prayer(ctx.author.id, ' '.join(args))
                await ctx.send(out)

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
                out = f'{item.title()} has been locked!'
            else:
                out = f'{item.title()} does not exist in your inventory. You must have it present to lock it'
            await ctx.send(out)

    @items.command(name='unlock')
    async def _item_unlock(self, ctx, *args):
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            item = ' '.join(args)
            if ctx.user_object.unlock_item(item):
                out = f'{item.title()} has been unlocked!'
            else:
                out = f'{item.title()} does not exist in your inventory. You must have it present to unlock it'
            await ctx.send(out)

    @commands.command()
    async def slayer(self, ctx):
        """Gives the user a slayer task."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            out = sh.get_task(ctx.guild.id, ctx.channel.id, ctx.user_object)
            await ctx.send(out)

    @commands.command()
    async def reaper(self, ctx):
        """Gives the user a reaper task."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            out = sh.get_reaper_task(ctx.guild.id, ctx.channel.id, ctx.author.id)
            await ctx.send(out)

    @commands.group(invoke_without_command=True, aliases=['grind', 'fring', 'dab', 'yeet'])
    async def kill(self, ctx, *args):
        from miniscape import adventures as adv
        """Lets the user kill monsters for a certain number or a certain amount of time."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            if len(args) > 0:
                monster = ''
                try:
                    number = users.parse_int(args[0])
                    monster = ' '.join(args[1:])
                    out = sh.get_kill(ctx.guild.id, ctx.channel.id, ctx.author.id, monster, number=number)
                except ValueError:
                    try:
                        length = users.parse_int(args[-1])
                        monster = ' '.join(args[:-1])
                        out = sh.get_kill(ctx.guild.id, ctx.channel.id, ctx.author.id, monster, length=length)
                    except ValueError:
                        monster = ' '.join(args)
                        if monster == 'myself':
                            with open('./resources/hotlines.txt', 'r') as f:
                                lines = f.read().splitlines()
                            out = '**If you need help, please call one of the following numbers**:\n'
                            for line in lines:
                                out += f'{line}\n'
                        else:
                            out = 'Error: there must be a number or length of kill in args.'
            else:
                if adv.is_on_adventure(ctx.author.id):
                    out = slayer.get_kill(ctx.guild.id, ctx.channel.id, ctx.author.id, 'GET_UPDATE')
                else:
                    out = 'args not valid. Please put in the form `[number] [monster name] [length]`'
            await ctx.send(out)

    @commands.command(aliases=['starter'])
    async def starter_gear(self, ctx):
        """Gives the user a set of bronze armour."""
        author: User = ctx.user_object
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            if author.combat_xp == 0:
                author.update_inventory(Counter([63, 66, 69, 70, 64, 72]))

                await ctx.send(f'Bronze set given to {author.plain_name}! You can see your items by typing `~inventory` in #bank '
                               f'and equip them by typing `~equip [item]`. You can see your current stats by typing '
                               f'`~me`. If you need help with commands, feel free to look at #welcome or ask around!')
            else:
                await ctx.send(f'You are too experienced to get the starter gear, {name}.')

    @commands.command(aliases=['bes', 'monsters'])
    async def bestiary(self, ctx, *args):
        """Shows a list of monsters and information related to those monsters."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            monster = ' '.join(args)
            if monster == '':
                messages = mon.print_list()
            else:
                messages = mon.print_monster(monster)
            await self.paginate(ctx, messages)

    @commands.command()
    async def chance(self, ctx, monsterid, dam=-1, acc=-1, arm=-1, cb=-1, xp=-1, num=100, dfire=False):
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            out = slayer.print_chance(ctx.author.id, monsterid, monster_dam=int(dam), monster_acc=int(acc),
                                      monster_arm=int(arm), monster_combat=int(cb), xp=int(xp), number=int(num),
                                      dragonfire=bool(dfire))
            await ctx.send(out)

    #@commands.command()
    async def claim(self, ctx, *args):
        # TODO: Come back to this. Honestly maybe leave it as is but adjust for user.update_inv?
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            try:
                number = int(args[0])
                item = ' '.join(args[1:])
            except ValueError:
                number = 1
                item = ' '.join(args)
            out = items.claim(ctx.author.id, item, number)
            await ctx.send(out)

    @commands.command(aliases=['cancle'])
    async def cancel(self, ctx):
        """Cancels your current action."""
        from miniscape import adventures as adv
        author: User = ctx.user_object

        if has_post_permission(ctx.guild.id, ctx.channel.id):
            try:
                task = adv.get_adventure(ctx.author.id)

                adventureid = task[0]
                if adventureid == '0':
                    if author.has_item_by_item(REAPER_TOKEN):
                        author.update_inventory(REAPER_TOKEN, remove=True)
                        adv.remove(ctx.author.id)
                        out = 'Slayer task cancelled!'
                    else:
                        out = 'Error: You do not have a reaper token.'
                elif adventureid == '1':
                    adv.remove(ctx.author.id)
                    out = 'Killing session cancelled!'
                elif adventureid == '2':
                    adv.remove(ctx.author.id)
                    out = 'Quest cancelled!'
                elif adventureid == '3':
                    adv.remove(ctx.author.id)
                    out = 'Gather cancelled!'
                elif adventureid == '4':
                    adv.remove(ctx.author.id)
                    out = 'Clue scroll cancelled!'
                elif adventureid == '5':
                    adv.remove(ctx.author.id)
                    out = 'Reaper task cancelled!'
                elif adventureid == '6':
                    adv.remove(ctx.author.id)
                    out = 'Runecrafting session cancelled!'
                else:
                    out = f'Error: Invalid Adventure ID {adventureid}'

            except NameError:
                out = 'You are not currently doing anything.'
            await ctx.send(out)

    @commands.command()
    async def compare(self, ctx, item1, item2):
        """Compares the stats of two items."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            out = item_helpers.compare(item1.lower(), item2.lower())
            await ctx.send(out)

    @commands.command(aliases=['stuatus'])
    async def status(self, ctx):
        """Says what you are currently doing."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            if adv.is_on_adventure(ctx.author.id):
                out = adv.print_adventure(ctx.author.id)
            else:
                out = 'You are not doing anything at the moment.'
            await ctx.send(out)

    @commands.group(aliases=['clues'], invoke_without_command=True)
    async def clue(self, ctx, difficulty):
        """Starts a clue scroll."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            if not difficulty.isdigit():
                difficulty_names = {
                    'easy': 1,
                    'medium': 2,
                    'hard': 3,
                    'elite': 4,
                    'master': 5
                }
                if difficulty not in set(difficulty_names.keys()):
                    await ctx.send(f'Error: {difficulty} not valid clue scroll difficulty.')
                    return
                else:
                    parsed_difficulty = difficulty_names[difficulty]
            else:
                if not (0 < int(difficulty) < 6):
                    await ctx.send(f'Error: {difficulty} not valid clue scroll difficulty.')
                    return
                else:
                    parsed_difficulty = int(difficulty)
            out = clue_helpers.start_clue(ctx.guild.id, ctx.channel.id, ctx.author.id, parsed_difficulty)
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
            if len(args) > 0:
                try:
                    number = int(args[0])
                    item = ' '.join(args[1:])
                except ValueError:
                    number = 1
                    item = ' '.join(args)
                out = item_helpers.buy(ctx.author.id, item, number=number)
                await ctx.send(out)

    @commands.command()
    async def sell(self, ctx, *args):
        """Sells the player's inventory for GasterCoin."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            try:
                number = users.parse_int(args[0])
                item = ' '.join(args[1:])
            except ValueError:
                number = 1
                item = ' '.join(args)
            out = item_helpers.sell(ctx.author.id, item, number=number)
            await ctx.send(out)

    #@commands.command()
    async def sellall(self, ctx, maxvalue=None):
        """Sells all items in the player's inventory (below a certain value) for GasterCoin."""
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

    #@commands.command()
    async def trade(self, ctx, *args):
        """Trades to a person a number of a given object for a given price."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            if len(args) < 4:
                await ctx.send('Arguments missing. Syntax is `~trade [name] [number] [item] [offer]`.')
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
            out = f'{items.SHOP_HEADER}{name.title()} wants to sell {name_member.mention} ' \
                  f'{items.add_plural(number, itemid)} for {offer_formatted} coins. To accept this offer, reply ' \
                  f'to this post with a :thumbsup:. Otherwise, this offer will expire in one minute.'
            msg = await ctx.send(out)
            await msg.add_reaction(THUMBS_UP_EMOJI)

            x = True
            while x:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60)
                    if str(reaction.emoji) == THUMBS_UP_EMOJI and user == name_member and reaction.message.id == msg.id:
                        price = {"0": offer}
                        users.update_inventory(name_member.id, price, remove=True)
                        users.update_inventory(ctx.author.id, price)
                        loot = {itemid: number}
                        users.update_inventory(ctx.author.id, loot, remove=True)
                        users.update_inventory(name_member.id, loot)

                        buyer_name = get_display_name(name_member)
                        await ctx.send(f'{items.SHOP_HEADER}{name.title()} successfully sold '
                                       f'{items.add_plural(number, itemid)} to {buyer_name} for '
                                       f'{offer_formatted} coins!')
                        x = False
                except asyncio.TimeoutError:
                    await msg.edit(content=f'One minute has passed and your offer has been cancelled.')
                    x = False
            else:
                ctx.bot.trade_manager.reset_trade(trade, ctx.author.id, name_member.id)

    @commands.command()
    async def ironmemememe(self, ctx):
        """Lets a user become an ironman, by the way."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            out = ':tools: __**IRONMAN**__ :tools:\n' \
                  'If you want to become an ironman, please react to this post with a :thumbsup:. ' \
                  'This will **RESET** your account and give you the ironman role. ' \
                  'You will be unable to trade with other players or gamble. ' \
                  'In return, you will be able to proudly display your status as an ironman, by the way.'
            msg = await ctx.send(out)
            await msg.add_reaction('\N{THUMBS UP SIGN}')

            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60)
                    if str(reaction.emoji) == THUMBS_UP_EMOJI and user == ctx.author and reaction.message.id == msg.id:
                        ctx.user_object.reset_account()
                        ctx.user_object.is_ironman = True
                        ctx.user_object.save()
                        ironman_role = discord.utils.get(ctx.guild.roles, name="Ironman")
                        await ctx.author.add_roles(ironman_role, reason='Wanted to become an ironmeme.')
                        name = get_display_name(ctx.author)
                        await msg.edit(content=f':tools: __**IRONMAN**__ :tools:\nCongratulations, {name}, you are now '
                                       'an ironman!')
                        return
                except asyncio.TimeoutError:
                    await msg.edit(content=f'Your request has timed out. Please retype the command to try again.')
                    return

    @commands.command()
    async def deironman(self, ctx):
        """Lets a user become an normal user."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            out = ':tools: __**IRONMAN**__ :tools:\n' \
                  'If you want to remove your ironman status, please react to this post with a :thumbsup:. ' \
                  'This will keep your account the same as it is right now, but you will be able to trade with ' \
                  'others. If you want to re-ironman, you can type `~ironman`, but you will have to reset your account.'
            msg = await ctx.send(out)
            await msg.add_reaction('\N{THUMBS UP SIGN}')

            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60)
                    if str(reaction.emoji) == THUMBS_UP_EMOJI and user == ctx.author and reaction.message.id == msg.id:
                        ctx.user_object.is_ironman = False
                        ctx.user_object.save()
                        ironman_role = discord.utils.get(ctx.guild.roles, name="Ironman")
                        await ctx.author.remove_roles(ironman_role, reason="No longer wants to be ironmeme.")
                        name = get_display_name(ctx.author)
                        await msg.edit(content=f':tools: __**IRONMAN**__ :tools:\nCongratulations, {name}, you are now '
                                               'a normal user!')
                        return
                except asyncio.TimeoutError:
                    await msg.edit(content=f'Your request has timed out. Please retype the command to try again.')
                    return

    @commands.group(invoke_without_command=True, aliases=['quest'])
    async def quests(self, ctx, *args, questid=None):

        if has_post_permission(ctx.guild.id, ctx.channel.id):
            try:
                qid = int(args[0])
                out = quest_helpers.print_details(ctx.user_object, qid)
                await ctx.send(out)
                return
            except ValueError:
                if args[0] == 'start':
                    messages = quest_helpers.start_quest(ctx.guild.id, ctx.channel.id, ctx.user_object, args[1])
                elif args[0] == 'incomplete':
                    messages = quest_helpers.print_list(ctx.user_object, args[0] == 'incomplete')
            except IndexError:
                messages = quest_helpers.print_list(ctx.user_object, incomplete=False)

            await self.paginate(ctx, messages)

    @commands.command()
    async def gather(self, ctx, *args):
        """Gathers items."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            if len(args) > 0:
                try:
                    number = users.parse_int(args[0])
                    item = ' '.join(args[1:])
                    out = craft_helpers.start_gather(ctx.guild.id, ctx.channel.id, ctx.user_object, item, number=number)
                except ValueError:
                    try:
                        length = users.parse_int(args[-1])
                        item = ' '.join(args[:-1])
                        out = craft_helpers.start_gather(ctx.guild.id, ctx.channel.id, ctx.user_object, item, length=length)
                    except ValueError:
                        out = 'Error: there must be a number or length of gathering in args.'
                await ctx.send(out)
            else:
                messages = craft_helpers.get_gather_list()
                await self.paginate(ctx, messages)

    @commands.group(aliases=['rc'])
    async def runecraft(self, ctx, *args):
        """Starts a runecrafting session."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            try:
                number = users.parse_int(args[0])
                if number >= MAX_PER_ACTION:
                    number = MAX_PER_ACTION
                rune = ' '.join(args[1:])
            except ValueError:
                number = 1
                rune = ' '.join(args)
            out = craft_helpers.start_runecraft(ctx.guild.id, ctx.channel.id, ctx.user_object, rune, number)
            await ctx.send(out)

    @runecraft.command(aliases=['pure'])
    async def _runecraft_pure(self, ctx, *args):
        """Starts a runecrafting session with pure essence."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            try:
                number = parse_name(args[0])
                if number >= MAX_PER_ACTION:
                    number = MAX_PER_ACTION
                rune = ' '.join(args[1:])
            except ValueError:
                number = 1
                rune = ' '.join(args)
            out = craft_helpers.start_runecraft(ctx.guild.id, ctx.channel.id, ctx.user_object, rune, number, pure=1)
            await ctx.send(out)

    @commands.group(invoke_without_command=True)
    async def vis(self, ctx, *args):
        """Lets the user guess the current vis combination."""
        author = ctx.user_object
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            if author.is_vis_complete:
                await ctx.send("You have already received vis wax today. Please wait until tomorrow to try again.")
                return

            if author.rc_level < 75:
                await ctx.send("You do not have a high enough runecrafting level to know how to use this machine.")

            runes = []
            if len(args) == 3:
                for rune in args:
                    runes.append(rune + " rune")
            elif len(args) == 6:
                runes.append(' '.join(args[0:1]))
                runes.append(' '.join(args[2:3]))
                runes.append(' '.join(args[4:5]))
            else:
                await ctx.send("Invalid number of arguments. Please enter the name of three runes.")
                return

            num_vis = vis.calc(ctx.author.id, runes)
            if type(num_vis) == str:
                await ctx.send(num_vis)
                return

            num_attempts = author.vis_attempts
            author.vis_attempts += 1
            author.save()
            users.update_user(ctx.author.id, num_attempts + 1, key=users.VIS_ATTEMPTS_KEY)
            out = f"{craft_helpers.GATHER_HEADER}With the runes {runes}, you can receive {num_vis} vis wax per " \
                  f"slot, respectively, for a total of {sum(num_vis)} vis wax. You have made {num_attempts + 1} " \
                  f"attempts today, meaning that you require {vis.calc_num(num_attempts + 1)} of each rune to make this many vis wax."
            await ctx.send(out)

    @vis.command(name='third')
    async def _vis_third(self, ctx):
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            if users.rc_level < 99:
                await ctx.send("You do not have a high enough runecrafting level to use this command")
            else:
                await ctx.send(f"Your third vis wax slot rune for today is {items.get_attr(vis.RUNEIDS[vis.calc_third_rune(ctx.author.id)])}.")

    @vis.command(name='use')
    async def _vis_use(self, ctx, *args):
        author = ctx.user_object
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            if author.is_vis_complete:
                await ctx.send("You have already received vis wax today. Please wait until tomorrow to try again.")
                return

            if author.rc_level < 75:
                await ctx.send("You do not have a high enough runecrafting level to know how to use this machine.")

            runes = []
            if len(args) == 3:
                for rune in args:
                    runes.append(rune + " rune")
            elif len(args) == 6:
                runes.append(' '.join(args[0:1]))
                runes.append(' '.join(args[2:3]))
                runes.append(' '.join(args[4:5]))
            else:
                await ctx.send("Invalid number of arguments. Please enter the name of three runes.")
                return

            num_vis = vis.calc(ctx.author.id, runes)
            if type(num_vis) == str:
                await ctx.send(num_vis)
                return
            
            num_runes = vis.calc_num(author.vis_attempts)
            loot = {}
            for rune in runes:
                itemid = items.find_by_name(rune)
                if users.item_in_inventory(ctx.author.id, itemid, num_runes):
                    loot[itemid] = num_runes
                else:
                    await ctx.send(f"You do not have enough runes to use this vis wax combination "
                                   f"({items.add_plural(num_runes, items.find_by_name(rune))})")
                    return

            author.update_inventory(loot, remove=True)
            author.update_inventory({'579' : round(sum(num_vis))})
            author.is_vis_complete = True
            author.save()

            out = f"{craft_helpers.GATHER_HEADER}With the runes {runes}, you received {num_vis} vis wax per " \
                  f"slot, respectively, for a total of {sum(num_vis)} vis wax. You have made {author.vis_attempts} " \
                  f"attempts today, meaning that you used {vis.calc_num(author.vis_attempts)} " \
                  f"of each rune to craft the vis wax."
            await ctx.send(out)

    @vis.command(name='shop')
    async def _vis_shop(self, ctx):
        """Prints the vis wax shop."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            await ctx.send(vis.shop_print())

    @vis.command(name='buy')
    async def _vis_buy(self, ctx, *args):
        """Buys an item from the vis wax shop."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            try:
                number = users.parse_int(args[0])
                item = ' '.join(args[1:])
            except ValueError:
                number = 1
                item = ' '.join(args)
            await ctx.send(vis.shop_buy(ctx.author.id, item, number))

    @commands.group(invoke_without_command=True, aliases=['recipe'])
    async def recipes(self, ctx, *args):
        """Prints a list of recipes a user can create."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            search = ' '.join(args)
            messages = craft_helpers.print_list(ctx.user_object, search)
            await self.paginate(ctx, messages)

    @recipes.command(name='info')
    async def _recipe_info(self, ctx, *args):
        """Lists the details of a particular recipe."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            recipe = ' '.join(args)
            out = craft_helpers.print_recipe(ctx.user_object, recipe)
            await ctx.send(out)

    @commands.command()
    async def craft(self, ctx, *args):
        """Crafts (a given number of) an item."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            try:
                number = users.parse_int(args[0])
                if number >= MAX_PER_ACTION:
                    number = MAX_PER_ACTION
                recipe = ' '.join(args[1:])
            except ValueError:
                number = 1
                recipe = ' '.join(args)
            out = craft_helpers.craft(ctx.user_object, recipe, n=number)
            await ctx.send(out)

    @commands.command(aliases=['cock', 'fry', 'grill', 'saute', 'boil'])
    async def cook(self, ctx, *args):
        """Cooks (a given amount of) an item."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            try:
                number = users.parse_int(args[0])
                if number >= MAX_PER_ACTION:
                    number = MAX_PER_ACTION
                food = ' '.join(args[1:])
            except ValueError:
                number = 1
                food = ' '.join(args)
            out = craft_helpers.cook(ctx.user_object, food, n=number)
            await ctx.send(out)

    @commands.command()
    async def balance(self, ctx, name=None):
        """Checks the user's balance."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            user: User = ctx.user_object
            item = Item.objects.get(name="coins")

            if name is None:
                amount = '{:,}'.format(user.get_item_by_item(item)[0].amount)
                name = get_display_name(ctx.author)
                await ctx.send(f'{name} has {amount} coins')
            elif name == 'universe':
                await ctx.send('As all things should be.')
            else:
                user = User.objects.filter(Q(name__icontains=name) | Q(nick__icontains=name))
                if not user:
                    await ctx.send(f'Name {name} not found in server.')
                elif len(user) > 1:
                    await ctx.send(f'Input {name} can refer to multiple people ({members})')
                else:
                    user = user[0]
                    amount = '{:,}'.format(user.get_item_by_item(item)[0].amount)
                    await ctx.send(f'{user.plain_name} has {amount} coins')


    @commands.command(aliases=['leaderboards'])
    async def leaderboard(self, ctx, *args):
        """Allows users to easily compare each others' stats."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            name = " ".join(args) if len(args) > 0 else None
            await self.print_leaderboard(ctx, name)

    async def print_leaderboard(self, ctx, name):
        """Prints the leaderboard and provides an interface for showing various leaderboards."""
        leaderboards = {}
        for key in users.LEADERBOARD_TITLES.keys():
            leaderboards[key] = users.get_values_by_account(key)

        msg = await ctx.send("Loading leaderboards...")

        leaderboard_messages = {}
        for key in users.LEADERBOARD_TITLES.keys():
            leaderboard = leaderboards[key]

            try:
                lower, upper = await self.get_leaderboard_range(ctx, name, leaderboard)
            except ValueError:
                continue

            out = users.LEADERBOARD_HEADER.replace("$KEY", users.LEADERBOARD_TITLES[key].title())
            out = out.replace("$EMOJI", users.LEADERBOARD_EMOJI[key])
            
            try:
                for i in range(lower, upper):
                    user_id, amount = leaderboard[i]
                    amount_formatted = '{:,}'.format(amount)
                    member = ctx.message.guild.get_member(user_id)
                    if member is not None:
                        username = get_display_name(member)
                    else:
                        username = f'User {user_id}'
                    out_user = f'**({1 + i}) {username}**: {amount_formatted} {users.LEADERBOARD_QUANTIFIERS[key]}\n'
                    # if key == 'total':
                    #     out_user = out_user.replace("$LEVEL", f"{users.xp_to_level(amount)}")
                    out += out_user
            except IndexError:
                pass

            leaderboard_messages[key] = out
            await msg.add_reaction(users.LEADERBOARD_EMOJI[key])
        await msg.edit(content=leaderboard_messages['total'])
        
        while True:
            reaction, user = await self.bot.wait_for('reaction_add')
            if user == ctx.author and reaction.message.id == msg.id:
                for key in users.LEADERBOARD_EMOJI.keys():
                    if str(reaction.emoji) == users.LEADERBOARD_EMOJI[key]:
                        await msg.edit(content=None)
                        await msg.edit(content=leaderboard_messages[key])

    async def get_leaderboard_range(self, ctx, name, leaderboard):
        """Gets the lower and upper bounds of a leaderboard and returns them as a tuple."""
        if name is None:
            leaderboard_range = (0, users.LEADERBOARD_LENGTH)
        elif name == 'bottom':
            leaderboard_range = (len(leaderboard) - users.LEADERBOARD_LENGTH, len(leaderboard))
        else:
            try:
                name_list = [x[0] for x in leaderboard]
                name_member = parse_name(ctx.message.guild, name)
                name_index = name_list.index(name_member.id)
                if name_index < 5:
                    lower = 0
                    upper = 10
                else:
                    lower = name_index - 5
                    upper = name_index + 5
                if name_index + 5 > len(leaderboard):
                    upper = len(leaderboard)
                    lower = len(leaderboard) - 10
                leaderboard_range = (lower, upper)
            except NameError:
                print(name)
                pass
            except ValueError:
                raise ValueError
        return leaderboard_range

    async def paginate(self, ctx, messages):
        """Provides an interface for printing a paginated set of messages."""
        if type(messages) == str:
            print(messages)
            await ctx.send(messages)
            return
        if len(messages) == 1:
            await ctx.send(messages[0])
            return

        current_page = 0
        out = messages[current_page]
        msg = await ctx.send(out)
        await msg.add_reaction(ARROW_LEFT_EMOJI)
        await msg.add_reaction(ARROW_RIGHT_EMOJI)

        while True:
            reaction, user = await self.bot.wait_for('reaction_add')
            if user == ctx.author and reaction.message.id == msg.id:

                if str(reaction.emoji) == ARROW_LEFT_EMOJI:
                    if current_page > 0:
                        current_page -= 1
                        out = messages[current_page]
                        out += f"\n{current_page + 1}/{len(messages)}"
                        await msg.edit(content=None)
                        await msg.edit(content=out)
                elif str(reaction.emoji) == ARROW_RIGHT_EMOJI:
                    if current_page < len(messages) - 1:
                        current_page += 1
                        out = messages[current_page] 
                        out += f"\n{current_page + 1}/{len(messages)}"
                        await msg.edit(content=None)
                        await msg.edit(content=out)

    async def reset_dailies(self):
        """Checks if the current time is a different day and resets everyone's daily progress."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed(): 
            try:
                with open('./resources/last_check.txt', 'r') as f:
                    last_check_string = f.read().splitlines()
                last_check_time = datetime.datetime.strptime(last_check_string[0], '%Y-%m-%d %H:%M:%S.%f')
            except FileNotFoundError as e:
                print(e)
                with open('./resources/last_check.txt', 'w+') as f:
                    f.write(f"{datetime.datetime.now()}\n")
                last_check_time = datetime.datetime.now()
            except Exception as e:
                 print(e)
            
            print(f"{last_check_time.date()} {datetime.datetime.now().date()}")
            if last_check_time.date() < datetime.datetime.now().date():
                try:
                    users.reset_dailies()
                    vis.update_vis()
                    with open('./resources/last_check.txt', 'w+') as f:
                        f.write(f"{datetime.datetime.now()}\n")
                except Exception as e:
                    print(e)
            await asyncio.sleep(60)

    async def check_adventures(self):
        """Check if any actions are complete and notifies the user if they are done."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            with open('./resources/debug.txt', 'a+') as f:
                f.write(f'Bot check at {datetime.datetime.now()}:\n')
            try:
                finished_tasks = adv.get_finished()
            except Exception as e:
                traceback.print_exc()
                traceback.print_exception(e)
                with open('./resources/debug.txt', 'a+') as f:
                    f.write(f'{e}\n')
                print(e)

            for task in finished_tasks:
                print(task)
                with open('./resources/debug.txt', 'a+') as f:
                    f.write(';'.join(task) + '\n')
                with open('./resources/finished_tasks.txt', 'a+') as f:
                    f.write(';'.join(task) + '\n')
                adventureid, userid, guildid, channelid = int(task[0]), int(task[1]), int(task[3]), int(task[4])
                bot_guild = self.bot.get_guild(guildid)
                try:
                    announcement_channel = cp.get_channel(guildid, cp.ANNOUNCEMENT_KEY)
                    bot_self = bot_guild.get_channel(int(announcement_channel))
                except KeyError:
                    bot_self = bot_guild.get_channel(channelid)
                person = bot_guild.get_member(int(userid))
                
                adventures = {
                    0: sh.get_result,
                    1: sh.get_kill_result,
                    2: quest_helpers.get_result,
                    3: craft_helpers.get_gather,
                    4: clue_helpers.get_clue_scroll,
                    5: sh.get_reaper_result,
                    6: craft_helpers.get_runecraft
                }
                try:
                    logging.getLogger(__name__).info(f"About  to call function for adventure {adventureid}")
                    out = adventures[adventureid](person, task[5:])
                    await bot_self.send(out)
                except Exception as e:
                    traceback.print_exc()
                    traceback.print_exception(e)
                    with open('./resources/debug.txt', 'a+') as f:
                        f.write(f'{e}\n')
                    print(e)
                print('done')
            await asyncio.sleep(TICK_SECONDS)


def setup(bot):
    """Adds the cog to the bot."""
    bot.add_cog(Miniscape(bot))
