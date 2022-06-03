from discord.ext import commands

import miniscape.command_helpers as ch
import miniscape.vis_helpers as vis_helpers
from cogs.cmd.common import has_post_permission


class VisCommands:

    @commands.group(invoke_without_command=True)
    async def vis(self, ctx, *args):
        """Lets the user guess the current vis combination."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
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
    async def _vis_third(self, ctx):
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            if ctx.user_object.rc_level < 99:
                await ctx.send("You do not have a high enough runecrafting level to use "
                               "this command.")
            else:
                third_rune = vis_helpers.get_vis_runes(ctx.user_object)[2][0]
                await ctx.send(f"Your third vis wax slot rune for today is: {third_rune.rune.name}.")

    @vis.command(name='use')
    async def _vis_use(self, ctx, *args):
        if has_post_permission(ctx.guild.id, ctx.channel.id):
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
    async def _vis_shop(self, ctx):
        """Prints the vis wax shop."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            await ctx.send(vis_helpers.shop_print())

    @vis.command(name='buy')
    async def _vis_buy(self, ctx, *args):
        """Buys an item from the vis wax shop."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            number, item = ch.parse_number_and_name(args)
            if item:
                await ctx.send(vis_helpers.shop_buy(ctx.user_object, item, number))
