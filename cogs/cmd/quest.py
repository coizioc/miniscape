from discord.ext import commands

import miniscape.quest_helpers as quest_helpers
from cogs.cmd.common import has_post_permission


class QuestCommands:

    @commands.group(invoke_without_command=True, aliases=['quest'])
    async def quests(self, ctx, *args, questid=None):
        """TODO: Add docstring."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            try:
                qid = int(args[0])
                out = quest_helpers.print_details(ctx.user_object, qid)
                await ctx.send(out)
                return
            except ValueError:
                if args[0] == 'start':
                    messages = quest_helpers.start_quest(
                        ctx.guild.id, ctx.channel.id, ctx.user_object, args[1])
                elif args[0] == 'incomplete':
                    messages = quest_helpers.print_list(ctx.user_object, args[0] == 'incomplete')
            except IndexError:
                messages = quest_helpers.print_list(ctx.user_object, incomplete=False)

            await self.paginate(ctx, messages)
