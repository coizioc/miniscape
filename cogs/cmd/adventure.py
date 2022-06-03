from discord.ext import commands

from cogs.cmd.common import has_post_permission
from miniscape import adventures as adv
from miniscape.itemconsts import REAPER_TOKEN
from miniscape.models import User


class AdventureCommands:

    @commands.command(aliases=['cancle'])
    async def cancel(self, ctx):
        """Cancels your current action."""
        author: User = ctx.user_object

        if has_post_permission(ctx.guild.id, ctx.channel.id):
            try:
                task = adv.get_adventure(ctx.author.id)

                adventureid = task[0]
                if adventureid == '0':
                    if author.has_item_by_item(REAPER_TOKEN):
                        author.update_inventory(REAPER_TOKEN, remove=True)
                        adv.remove(ctx.author.id)
                        out = 'Slayer task cancelled!'
                    else:
                        out = 'Error: You do not have a reaper token.'
                elif adventureid == '1':
                    adv.remove(ctx.author.id)
                    out = 'Killing session cancelled!'
                elif adventureid == '2':
                    adv.remove(ctx.author.id)
                    out = 'Quest cancelled!'
                elif adventureid == '3':
                    adv.remove(ctx.author.id)
                    out = 'Gather cancelled!'
                elif adventureid == '4':
                    adv.remove(ctx.author.id)
                    out = 'Clue scroll cancelled!'
                elif adventureid == '5':
                    adv.remove(ctx.author.id)
                    out = 'Reaper task cancelled!'
                elif adventureid == '6':
                    adv.remove(ctx.author.id)
                    out = 'Runecrafting session cancelled!'
                else:
                    out = f'Error: Invalid Adventure ID {adventureid}'

            except NameError:
                out = 'You are not currently doing anything.'
            await ctx.send(out)

    @commands.command(aliases=['stuatus'])
    async def status(self, ctx):
        """Says what you are currently doing."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            if adv.is_on_adventure(ctx.author.id):
                out = adv.print_adventure(ctx.author.id)
            else:
                out = 'You are not doing anything at the moment.'
            await ctx.send(out)
