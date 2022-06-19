from discord.ext import commands

from cogs.cmd.checks import can_post
from miniscape import craft_helpers


class RunecraftCommands:

    @commands.group(aliases=["rc"], invoke_without_command=True)
    @can_post()
    async def runecraft(self, ctx, *args):
        await ctx.reply(mention_author=False, embed=craft_helpers.start_runecraft(ctx, *args))

    @runecraft.command(name='list')
    @can_post()
    async def _rc_list(self, ctx, *args):
        await ctx.send(embed=craft_helpers.list_runes())

    @runecraft.command(aliases=['pure'])
    @can_post()
    async def _runecraft_pure(self, ctx, *args):
        """Starts a runecrafting session with pure essence."""
        await ctx.reply(mention_author=False, embed=craft_helpers.start_runecraft(ctx, *args, pure=True))

