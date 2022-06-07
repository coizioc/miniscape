from discord.ext import commands

import miniscape.command_helpers as ch
import miniscape.slayer_helpers as sh
from cogs.cmd.common import has_post_permission


class CombatCommands:

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
        """Lets the user kill monsters for a certain number or a certain amount of time."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            number, monster, length = ch.parse_number_name_length(args)
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
                    out = sh.get_kill(
                        ctx.guild.id, ctx.channel.id, ctx.author.id, monster, number=number)
                elif length:
                    out = sh.get_kill(
                        ctx.guild.id, ctx.channel.id, ctx.author.id, monster, length=length)
                else:
                    out = 'Error: there must be a number or length of kill in args.'
            else:
                out = 'Arguments not valid. Please put in the form `[number] [monster name] [length]`'
            await ctx.send(out)