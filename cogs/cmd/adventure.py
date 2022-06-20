import json
from collections import Counter

import discord
from discord.ext import commands

from cogs.cmd.checks import can_post
from errors import AdventureNotFoundError
from mbot import MiniscapeBotContext
from miniscape import adventures as adv
from miniscape.itemconsts import REAPER_TOKEN
from miniscape.models import User, Task, Quest


def _get_adv_cancel_text_from_database(ctx: MiniscapeBotContext, task: Task) -> str:
    if task.type == "runecraft":
        task.delete()
        return f"{ctx.user_object.mention}, your runecrafting session has been cancelled!"

    if task.type == "quest":
        task.delete()
        quest = Quest.objects.get(id=json.loads(task.extra_data)["quest_id"])
        return f"{ctx.user_object.mention}, you are no longer doing the quest {quest.name}"

    if task.type == "gather":
        task.delete()
        return f"{ctx.user_object.mention}, your gathering session has been cancelled!"

    if task.type == "kill":
        task.delete()
        return f"{ctx.user_object.mention}, your killing session has been cancelled!"

    if task.type == "slayer":
        if ctx.user_object.has_item_by_item(REAPER_TOKEN):
            ctx.user_object.update_inventory(Counter({REAPER_TOKEN: 1}), remove=True)
            task.delete()
            return f"{ctx.user_object.mention}, your slayer task has been cancelled!"
        return f"{ctx.user_object.mention}, you need a reaper token in order to cancel a slayer task"


def _get_adv_text_from_file(ctx: MiniscapeBotContext, task) -> str:
    author: User = ctx.user_object
    adventureid = task[0]
    if adventureid == '0':
        if author.has_item_by_item(REAPER_TOKEN):
            author.update_inventory(REAPER_TOKEN, remove=True)
            adv.remove(ctx.author.id)
            return 'Slayer task cancelled!'
        else:
            return 'Error: You do not have a reaper token.'
    elif adventureid == '1':
        adv.remove(ctx.author.id)
        return 'Killing session cancelled!'
    elif adventureid == '2':
        adv.remove(ctx.author.id)
        return 'Quest cancelled!'
    elif adventureid == '3':
        adv.remove(ctx.author.id)
        return 'Gather cancelled!'
    elif adventureid == '4':
        adv.remove(ctx.author.id)
        return 'Clue scroll cancelled!'
    elif adventureid == '5':
        adv.remove(ctx.author.id)
        return 'Reaper task cancelled!'
    elif adventureid == '6':
        adv.remove(ctx.author.id)
        return 'Runecrafting session cancelled!'
    else:
        return f'Error: Invalid Adventure ID {adventureid}'


class AdventureCommands:

    @commands.command(aliases=['cancle'])
    @can_post()
    async def cancel(self, ctx: MiniscapeBotContext):
        """Cancels your current action."""
        out = discord.Embed(type="rich", description="", title="Cancel Result")

        try:
            task = adv.get_adventure(ctx.author.id)
        except AdventureNotFoundError:
            out.description = f"{ctx.user_object.mention}, you are not currently doing anything."
            await ctx.reply(mention_author=False, embed=out)
            return

        if type(task) == list:
            out.description = _get_adv_text_from_file(ctx, task)
        else:
            out.description = _get_adv_cancel_text_from_database(ctx, task)

        await ctx.reply(mention_author=False, embed=out)

    @commands.command(aliases=['stuatus', 'statussy'])
    @can_post()
    async def status(self, ctx):
        """Says what you are currently doing."""
        out = discord.Embed(title="Current Status", type="rich", description="")
        if adv.is_on_adventure(ctx.author.id):
            out.description += adv.print_adventure(ctx.author.id)
        else:
            out.description = 'You are not doing anything at the moment.'
        await ctx.reply(mention_author=False, embed=out)
