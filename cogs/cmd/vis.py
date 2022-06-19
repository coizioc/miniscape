from discord.ext import commands

import miniscape.vis_helpers as vis_helpers
import utils.command_helpers
from cogs.cmd.checks import can_post


class VisCommands:

    @commands.group(invoke_without_command=True)
    @can_post()
    async def vis(self, ctx, *args):
        """Lets the user guess the current vis combination."""
        author = ctx.user_object
        if author.is_vis_complete:
            await ctx.send("You have already received vis wax today. "
                           "Please wait until tomorrow to try again.")
            return
        if author.rc_level < 75:
            await ctx.send("You do not have a high enough runecrafting level to know how to "
                           "use this machine.")
            return

        out = vis_helpers.print_vis_result(author, args)
        await ctx.send(out)

    @vis.command(name='third')
    @can_post()
    async def _vis_third(self, ctx):
        if ctx.user_object.rc_level < 99:
            await ctx.send("You do not have a high enough runecrafting level to use "
                           "this command.")
        else:
            third_rune = vis_helpers.get_vis_runes(ctx.user_object)[2][0]
            await ctx.send(f"Your third vis wax slot rune for today is: {third_rune.rune.name}.")

    @vis.command(name='use')
    @can_post()
    async def _vis_use(self, ctx, *args):
        author = ctx.user_object
        if author.is_vis_complete:
            await ctx.send("You have already received vis wax today. "
                           "Please wait until tomorrow to try again.")
            return
        if author.rc_level < 75:
            await ctx.send("You do not have a high enough runecrafting level to know how to "
                           "use this machine.")
            return

        out = vis_helpers.print_vis_result(author, args, use=True)
        await ctx.send(out)

    @vis.command(name='shop')
    @can_post()
    async def _vis_shop(self, ctx):
        """Prints the vis wax shop."""
        await ctx.send(vis_helpers.shop_print())

    @vis.command(name='buy')
    @can_post()
    async def _vis_buy(self, ctx, *args):
        """Buys an item from the vis wax shop."""
        number, item = utils.command_helpers.parse_number_and_name(args)
        if item:
            await ctx.send(vis_helpers.shop_buy(ctx.user_object, item, number))
