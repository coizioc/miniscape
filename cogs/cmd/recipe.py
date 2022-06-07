from discord.ext import commands

from cogs.cmd.common import has_post_permission
from miniscape import craft_helpers


class RecipeCommands:

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
