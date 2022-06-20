import discord
from discord.ext import commands

from cogs.cmd.checks import can_post, is_in_admin_channel, is_admin
from mbot import MiniscapeBotContext
from miniscape.adventures import get_list
from miniscape.models import Task, User


class AdminCommands:

    @commands.command()
    @can_post()
    @is_admin()
    @is_in_admin_channel()
    async def statusall(self, ctx: MiniscapeBotContext, *args):
        out = discord.Embed(title="statusall", type="rich", description="")
        for task in Task.objects.all():
            out.description += str(task) + "\n\n"

        for task in get_list():
            user = User.objects.get(id=task[1])
            out.description += f"User {user.nick} is performing adventure type {task[0]} until {task[2]}. Extra" \
                               f"args: {str(args[5:])}\n\n"
        await ctx.reply(mention_author=False, embed=out)
