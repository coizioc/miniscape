from discord.ext import commands

from cogs.cmd.checks import can_post
from miniscape import craft_helpers


class RecipeCommands:

    @commands.group(invoke_without_command=True, aliases=['recipe'])
    @can_post()
    async def recipes(self, ctx, *args):
        """Prints a list of recipes a user can create."""
        search = ' '.join(args)
        messages = craft_helpers.print_list(ctx.user_object, search)
        await self.paginate(ctx, messages)

    @recipes.command(name='info')
    @can_post()
    async def _recipe_info(self, ctx, *args):
        """Lists the details of a particular recipe."""
        recipe = ' '.join(args)
        out = craft_helpers.print_recipe(ctx.user_object, recipe)
        await ctx.send(out)
