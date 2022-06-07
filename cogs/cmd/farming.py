from discord.ext import commands

from cogs.cmd.common import has_post_permission
from mbot import MiniscapeBotContext


class FarmingCommands:
    @commands.group()
    async def farm(self, ctx):
        pass

    @farm.group(name="plant", aliases=["p"])
    @commands.check(has_post_permission)
    async def _farm_plant(self, ctx: MiniscapeBotContext, *args):
        ctx.bot.farm_manager.plant(ctx, args)

    @farm.group(name="harvest", aliases=["h"])
    @commands.check(has_post_permission)
    async def _farm_harvest(self, ctx: MiniscapeBotContext, *args):
        ctx.bot.farm_manager.harvest(ctx, args)

    @farm.group(name="check", aliases=["ch"])
    @commands.check(has_post_permission)
    async def _farm_check(self, ctx: MiniscapeBotContext, *args):
        ctx.bot.farm_manager.check(ctx, args)

    @farm.group(name="clear", aliases=["cl"])
    @commands.check(has_post_permission)
    async def _farm_clear(self, ctx: MiniscapeBotContext, *args):
        ctx.bot.farm_manager.check(ctx, args)
