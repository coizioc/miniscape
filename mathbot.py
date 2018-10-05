"""Runs bots for a Discord server."""
import os
import sys
import traceback

from discord.ext import commands

import config


def extensions_generator():
    """Returns a generator for all cog files that aren't in do_not_use."""
    cog_path = "./cogs"
    do_not_use = ["__init__.py", "__pycache__", 'cap.py', 'pet.py', 'reddit.py', 'rs.py',
                  'solver.py', 'stats.py', 'telos.py', "memers.py", 'resources']
    do_use = ['miniscape.py', 'other.py', 'admin.py']
    for cog in os.listdir(cog_path):
        if cog in do_use:
            yield f"cogs.{cog[:-3]}"
    # use = ["stats.py"]
    # for cog in os.listdir(cog_path):
    #     if cog in use:
    #         yield f"cogs.{cog[:-3]}"

def submodules_generator():
    """Returns a generator for all submodule add-ons."""
    sub_path = "./subs"
    do_not_use = ["solver.py", 'ping.py', 'pokemon.py', 'gastercoin.py']
    for item in os.listdir(sub_path):
        path = os.path.join(sub_path, item)
        if item not in do_not_use:
            for sub in os.listdir(path):
                if sub == f"{item}.py" and sub not in do_not_use:
                    yield f"subs.{item}.{sub[:-3]}"
    # use = []
    # for item in os.listdir(sub_path):
    #     path = os.path.join(sub_path, item)
    #     if item in use:
    #         for sub in os.listdir(path):
    #             if sub == f"{item}.py" and sub in use:
    #                 yield f"subs.{item}.{sub[:-3]}"

DESCRIPTION = "A bot that runs a basic role-playing game."

# log = logging.getLogger(__name__)

class MathBot(commands.Bot):
    """Defines the mathbot class and functions."""

    def __init__(self):
        super().__init__(command_prefix=["~", "%"], description=DESCRIPTION)
        self.default_nick = "Miniscape"
        self.add_command(self.load)
        self.remove_command('help')

        for extension in extensions_generator():
            try:
                self.load_extension(extension)
                print(f"Successfully loaded extension {extension}.")
            except Exception:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

        for submodule in submodules_generator():
            try:
                self.load_extension(submodule)
                print(f"Successfully loaded submodule {submodule}.")
            except Exception:
                print(f'Failed to load submodule {submodule}.', file=sys.stderr)
                traceback.print_exc()

    async def on_ready(self):
        """Prints bot initialization info"""
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self, message):
        """Handles commands based on messages sent"""
        if message.author.bot:
            return
        if message.content.startswith('~help') or message.content.startswith('%help'):
            await message.channel.send('A tutorial and a list of commands can be found at '
                                       'https://github.com/coizioc/math-bot/blob/master/README.md')
        await self.process_commands(message)

    def run(self):
        """Runs the bot with the token from the config file."""
        super().run(config.token, reconnect=True)

    async def on_member_update(self, before, after):
        """Resets bot's nickname anytime it is changed."""
        if before.id == self.user.id and before.nick != after.nick:
            await after.edit(nick=self.default_nick)

    @commands.command()
    async def load(self, ctx, extension):
        """Loads a specified extension into the bot."""
        try:
            self.load_extension(extension)
            await ctx.send(f"Successfully loaded extension {extension}.")
        except Exception:
            await ctx.send(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

