import discord
from discord.ext import commands

from cogs.cmd.checks import can_post
from mbot import MiniscapeBotContext
from miniscape import quest_helpers, craft_helpers, monster_helpers, item_helpers, prayer_helpers

ALL_CATEGORIES = ["monster", "item", "recipe", "quest", "pray", "prayer",
                  "m", "i", "r", "q", "p"]


class GeneralCommands:

    @commands.command()
    @can_post()
    async def test(self, ctx: MiniscapeBotContext, *args):
        await ctx.reply(embed=discord.Embed(title="YOLO", type="rich"))

    @commands.command()
    @can_post()
    async def ree(self, ctx, *args):
        await ctx.send("<:reet:479701958916309012>")

    @commands.command(aliases=["s"])
    @can_post()
    async def search(self, ctx: MiniscapeBotContext, *args):
        """The ~search or ~s command is for searching for various things in miniscape. For example, one
        might search for quests, or monsters, or recipes, or items. valid use is like
        `~search monster queen`, this will do a string search on 'queen' for the name and any nicknames
        valid search categories are:
        - monster | m
        - item | i
        - recipe | r
        - quest | q
        - prayer | p

        If the second arg (the word coming after `~search` isn't one of those, it will attempt to do
        a broad search across all 5 and return the results in a nice way"""
        if len(args) == 0:
            await ctx.send("You must specify a category or a search term")
            return

        msgs = []
        global_search = False
        search_term = ' '.join(args[1:])

        if args[0] not in ALL_CATEGORIES:
            search_term = ' '.join(args)
            global_search = True
            msgs.append("No category specified, searching across everything... \n")

        if len(search_term) < 3 and global_search:
            await ctx.send("Search term must be at least three characters")
            return

        monsters = items = recipes = quests = prayers = []

        if global_search or args[0] in ["monster", "m"]:
            monsters = monster_helpers.print_list(search=search_term, allow_empty=False)
            if monsters: monsters[-1] += "\n"
        if global_search or args[0] in ["item", "i"]:
            items = item_helpers.print_all_items(search_term, allow_empty=False)
            if items: items[-1] += "\n"
        if global_search or args[0] in ["recipe", "r"]:
            recipes = craft_helpers.print_list(ctx.user_object, search_term, filter_quests=False, allow_empty=False)
            if recipes: recipes[-1] += "\n"
        if global_search or args[0] in ["quest", "q"]:
            quests = quest_helpers.print_list(ctx.user_object, search=search_term, get_stats=False, allow_empty=False, ignore_req=True)
            if quests: quests[-1] += "\n"
        if global_search or args[0] in ["pray", "prayer", "p"]:
            prayers = prayer_helpers.print_list("", search_term, allow_empty=False)
            if prayers: prayers[-1] += "\n"

        msgs = self._merge_search_results(msgs, monsters, items, recipes, quests, prayers)
        if not msgs or not msgs[0]:
            msgs = ["Unable to find anything that matches your search query."]
        await self.paginate(ctx, msgs)

    @staticmethod
    def _merge_search_results(*args):
        """ Takes a bunch of lists of messages and merges them into one list with each message being (hopefully)
        1800-2000 characters so that it fits in the discord text limit of 2000 characters. Ideal for use when some
        of the lists have single small messages as it reduces the number of messages we need to send, meaning we won't
        get rate limited as easily. In the future, this would likely be better done with emoji-based pagination"""
        final_result = []
        curr_msg = ""

        """Run through a copy of the args tuple. for each list do the following:
        - if curr_msg isn't an empty string and there's an item in the list, check to see if they can merge into a 
          single message
          - if possible, merge them. If not, add curr_msg to final_result and then proceed to below
        - if curr_msg is an empty string, set it to the last item in the list and append everything else into the final result
        - """
        for i, l in enumerate(args[:]):
            if len(curr_msg) >= 1900:
                final_result.append(curr_msg)
                curr_msg = ""

            if l:
                if len(l) > 1:
                    if curr_msg:
                        final_result.append(curr_msg)
                    final_result.extend(l)
                    curr_msg = final_result.pop()
                else:
                    if len(curr_msg) + len(l[0]) < 2000:
                        curr_msg += l[0]
                    else:
                        final_result.append(curr_msg)
                        curr_msg = l[0]

        final_result.append(curr_msg)
        return final_result
