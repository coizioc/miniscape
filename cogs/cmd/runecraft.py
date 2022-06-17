from discord.ext import commands

import utils.command_helpers
from cogs.cmd.common import has_post_permission
from config import MAX_PER_ACTION
from miniscape import craft_helpers


class RunecraftCommands:

    @commands.group(aliases=['rcold'], invoke_without_command=True)
    async def runecraft_old(self, ctx, *args):
        """Starts a runecrafting session."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            number, rune = utils.command_helpers.parse_number_and_name(args)
            if number and rune:
                out = craft_helpers.start_runecraft_old(
                    ctx.guild.id, ctx.channel.id, ctx.user_object, rune, min(number, MAX_PER_ACTION))
                await ctx.send(out)

    @runecraft_old.command(aliases=['pure'])
    async def _runecraft_pure(self, ctx, *args):
        """Starts a runecrafting session with pure essence."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            number, rune = utils.command_helpers.parse_number_and_name(args)
            if number and rune:
                out = craft_helpers.start_runecraft_old(
                    ctx.guild.id, ctx.channel.id, ctx.user_object, rune, min(number, MAX_PER_ACTION), pure=1)
                await ctx.send(out)

    @commands.group(aliases=["rc"], invoke_without_command=True)
    async def runecraft(self, ctx, *args):
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            await ctx.reply(mention_author=False, embed=craft_helpers.start_runecraft(ctx, *args))

    @runecraft.command(name='list')
    async def _rc_list(self, ctx, *args):
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            await ctx.send(embed=craft_helpers.list_runes())

    @runecraft.command(aliases=['pure'])
    async def _runecraft_pure(self, ctx, *args):
        """Starts a runecrafting session with pure essence."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            await ctx.reply(mention_author=False, embed=craft_helpers.start_runecraft(ctx, *args, pure=True))

