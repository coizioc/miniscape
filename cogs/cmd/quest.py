from discord.ext import commands

import miniscape.quest_helpers as quest_helpers
from cogs.cmd.checks import can_post
from mbot import MiniscapeBotContext


class QuestCommands:

    @commands.group(invoke_without_command=True, aliases=['quest'])
    @can_post()
    async def quests(self, ctx: MiniscapeBotContext, *args, questid=None):
        try:
            qid = int(args[0])
            out = quest_helpers.print_details(ctx.user_object, qid)
            await ctx.send(out)
            return
        except ValueError:
            if args[0] == 'start':
                out = quest_helpers.start_quest(ctx, args[1])
                await ctx.reply(mention_author=False, embed=out)
                return
            elif args[0] == 'incomplete':
                messages = quest_helpers.print_list(ctx.user_object, args[0] == 'incomplete')
        except IndexError:
            messages = quest_helpers.print_list(ctx.user_object, incomplete=False)

        await self.paginate(ctx, messages)
