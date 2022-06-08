
from discord.ext import commands
import miniscape.clue_helpers as clue_helpers
from cogs.cmd.common import has_post_permission

difficulty_names = {
    'easy': 1,
    'medium': 2,
    'hard': 3,
    'elite': 4,
    'master': 5
}

class ClueCommands:

    @commands.group(aliases=['clues'], invoke_without_command=True)
    async def clue(self, ctx, difficulty):
        """Starts a clue scroll."""
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            if not difficulty.isdigit():
                if difficulty not in set(difficulty_names.keys()):
                    await ctx.send(f'Error: {difficulty} not valid clue scroll difficulty.')
                    return
                parsed_difficulty = difficulty_names[difficulty]
            else:
                if not 0 < int(difficulty) < 6:
                    await ctx.send(f'Error: {difficulty} not valid clue scroll difficulty.')
                    return
                parsed_difficulty = int(difficulty)
            out = clue_helpers.start_clue(ctx.guild.id, ctx.channel.id, ctx.author.id,
                                          parsed_difficulty)
            await ctx.send(out)

    @clue.command(name='loot')
    async def _clue_loot(self, ctx, difficulty):
        if has_post_permission(ctx.guild.id, ctx.channel.id):
            if difficulty not in set(difficulty_names.keys()):
                await ctx.send(f'Error: {difficulty} not valid clue scroll difficulty.')
                return
            parsed_difficulty = difficulty_names[difficulty]
        item = Item.objects.get(name__iexact=difficulty)
        table = clue_helpers.get_loot_table(item)
        out = ""
        for i in table:
            out += f"{i.loot_item}\n"
        
        await ctx.send(out)