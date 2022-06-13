"""Implements commands related to running a freemium-style text-based RPG."""
import asyncio
import datetime
import logging
import traceback

from discord.ext import commands

import miniscape.clue_helpers as clue_helpers
import miniscape.command_helpers as ch
import miniscape.monster_helpers as mon
import miniscape.periodicchecker_helpers as pc_helpers
import miniscape.quest_helpers as quest_helpers
import miniscape.slayer_helpers as sh
from cogs.cmd import *
from cogs.cmd.channel_permissions import get_channel, ANNOUNCEMENT_KEY
from cogs.cmd.common import has_post_permission
from config import ARROW_LEFT_EMOJI, ARROW_RIGHT_EMOJI, THUMBS_UP_EMOJI, TICK_SECONDS, MAX_PER_ACTION
from miniscape import adventures as adv, craft_helpers


class Miniscape(commands.Cog,
                UserCommands,
                QuestCommands,
                VisCommands,
                ItemCommands,
                CombatCommands,
                RunecraftCommands,
                RecipeCommands,
                AdventureCommands,
                GeneralCommands):
    """Defines Miniscape commands."""

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.check_adventures())
        self.bot.loop.create_task(self.reset_dailies())

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
                parsed_difficulty = difficulty_names[difficulty]
            else:
                if not 0 < int(difficulty) < 6:
                    await ctx.send(f'Error: {difficulty} not valid clue scroll difficulty.')
                    return
                parsed_difficulty = int(difficulty)
            out = clue_helpers.start_clue(ctx.guild.id, ctx.channel.id, ctx.author.id,
                                          parsed_difficulty)
            await ctx.send(out)

    @commands.command()
    async def gather(self, ctx, *args):
        """Gathers items."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            number, name, length = ch.parse_number_name_length(args)
            if name:
                if number:
                    out = craft_helpers.start_gather(
                        ctx.guild.id, ctx.channel.id, ctx.user_object, name, number=number)
                elif length:
                    out = craft_helpers.start_gather(
                        ctx.guild.id, ctx.channel.id, ctx.user_object, name, length=length)
                else:
                    out = "You must provide either a number or length."
                await ctx.send(out)
            else:
                messages = craft_helpers.get_gather_list()
                await self.paginate(ctx, messages)

    @commands.command()
    async def craft(self, ctx, *args):
        """Crafts (a given number of) an item."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            number, rec = ch.parse_number_and_name(args)
            if number and rec:
                out = craft_helpers.craft(ctx.user_object, rec, n=min(number, MAX_PER_ACTION))
                await ctx.send(out)

    @commands.command(aliases=['cock', 'fry', 'grill', 'saute', 'boil'])
    async def cook(self, ctx, *args):
        """Cooks (a given amount of) an item."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            number, food = ch.parse_number_and_name(args)
            if number and food:
                out = craft_helpers.cook(ctx.user_object, food, n=min(number, MAX_PER_ACTION))
                await ctx.send(out)


    async def confirm(self, ctx, msg, _, timeout=300):
        """Asks the user to confirm an action, and returns whether they confirmed or not."""
        await msg.add_reaction('\N{THUMBS UP SIGN}')

        while True:
            try:
                reaction, person = await self.bot.wait_for('reaction_add', timeout=timeout)
                if (str(reaction.emoji) == THUMBS_UP_EMOJI and person == ctx.author and
                        reaction.message.id == msg.id):
                    return True
            except asyncio.TimeoutError:
                await msg.edit(content=f'Your request has timed out. Please retype the command '
                                       'to try again.')
                return False

    async def paginate(self, ctx, messages):
        """Provides an interface for printing a paginated set of messages."""
        if isinstance(messages, str):
            print(messages)
            await ctx.send(messages)
            return
        else:
            for msg in messages:
                await ctx.send(msg)
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
            reaction, person = await self.bot.wait_for('reaction_add')
            if person == ctx.author and reaction.message.id == msg.id:

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
            if pc_helpers.is_next_day():
                pc_helpers.reset_dailies()
                print('dailies updated successfully')
            await asyncio.sleep(TICK_SECONDS)

    async def check_adventures(self):
        """Check if any actions are complete and notifies the user if they are done."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            with open('./resources/debug.txt', 'a+') as debug_file:
                debug_file.write(f'Bot check at {datetime.datetime.now()}:\n')

            finished_tasks = []
            try:
                finished_tasks = adv.get_finished()
            except Exception as adv_exception:
                traceback.print_exc()
                with open('./resources/debug.txt', 'a+') as debug_file:
                    debug_file.write(f'{adv_exception}\n')
                print(adv_exception)

            for task in finished_tasks:
                print(task)
                with open('./resources/debug.txt', 'a+') as debug_file:
                    debug_file.write(';'.join(task) + '\n')
                with open('./resources/finished_tasks.txt', 'a+') as task_file:
                    task_file.write(';'.join(task) + '\n')
                adventureid = int(task[0])
                userid = int(task[1])
                guildid = int(task[3])
                channelid = int(task[4])
                bot_guild = self.bot.get_guild(guildid)
                try:
                    announcement_channel = get_channel(guildid, ANNOUNCEMENT_KEY)
                    bot_self = bot_guild.get_channel(int(announcement_channel))
                except KeyError:
                    bot_self = bot_guild.get_channel(channelid)
                person = int(userid)

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
                    logging.getLogger(__name__).info(f"About to call function for adventure "
                                                     f"{adventureid}")
                    out = adventures[adventureid](person, task[5:])
                    await bot_self.send(out)
                except Exception as miniscape_exception:
                    traceback.print_exc()
                    with open('./resources/debug.txt', 'a+') as debug_file:
                        debug_file.write(f'{miniscape_exception}\n')
                    print(miniscape_exception)
                print('done')
            await asyncio.sleep(TICK_SECONDS)


def setup(bot):
    """Adds the cog to the bot."""
    bot.add_cog(Miniscape(bot))
