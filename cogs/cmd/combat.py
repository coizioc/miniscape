import discord
from discord.ext import commands

import miniscape.slayer_helpers as sh
import utils.command_helpers
from cogs.cmd.checks import can_post
from mbot import MiniscapeBotContext


class CombatCommands:

    @commands.command()
    @can_post()
    async def slayer(self, ctx):
        """Gives the user a slayer task."""
        out = sh.get_slayer_task(ctx)
        await ctx.reply(mention_author=False, embed=out)

    @commands.command()
    @can_post()
    async def reaper(self, ctx):
        """Gives the user a reaper task."""
        out = sh.get_reaper_task_new(ctx)
        await ctx.reply(mention_author=False, embed=out)

    @commands.group(invoke_without_command=True, aliases=['grind', 'fring', 'dab', 'yeet'])
    @can_post()
    async def kill(self, ctx: MiniscapeBotContext, *args):
        """Lets the user kill monsters for a certain number or a certain amount of time."""
        number, monster, length = utils.command_helpers.parse_number_name_length(args)
        if monster:
            if monster == 'myself':
                messages = []
                with open('./resources/hotlines.txt', 'r') as hotlines_file:
                    lines = hotlines_file.read().splitlines()
                out = '**If you need help, please call one of the following ' \
                      'numbers**:\n'
                i = 1
                for line in lines:
                    out += f'{line}\n'
                    if i % 20 == 0:
                        messages.append(out)
                        out = '**If you need help, please call one of the following ' \
                              'numbers**:\n'
                    i += 1
                messages.append(out)
                await self.paginate(ctx, messages)
                return
            elif number:
                out = sh.start_kill(ctx, monster, number=number)
            elif length:
                out = sh.start_kill(ctx, monster, length=length)
            else:
                out = discord.Embed(title="ERROR", type="rich",
                                    description='Error: there must be a number or length of kill in args.')
        else:
            out = discord.Embed(title="ERROR", type="rich",
                               description='Arguments not valid. Please put in the form '
                                           '`~kill [number] [monster name]` or '
                                           '`~kill [monster name] [length in minutes]`')
        await ctx.reply(mention_author=False, embed=out)
