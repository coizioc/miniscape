#! /usr/bin/env python3
"""Runs bots for a Discord server."""
# These lines allow us to use Django models
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "miniscapebot.settings")
import django
django.setup()

import logging
import sys
import asyncio
import traceback
from django.core.exceptions import ObjectDoesNotExist
from discord.ext import commands
from discord.ext.commands import CheckFailure
from miniscape.models import User
import config
from pythonjsonlogger import jsonlogger


def extensions_generator():
    """Returns a generator for all cog files that aren't in do_not_use."""
    cog_path = "./cogs"
    do_not_use = ['errors', 'helper', 'managers', 'cmd', '__pycache__', 'test.py', '__init__.py']
    for cog in os.listdir(cog_path):
        if cog not in do_not_use:
            yield f"cogs.{cog[:-3]}"


class MiniscapeBot(commands.Bot):
    """Defines the miniscapebot class and functions."""

    def __init__(self):
        description = "A bot that runs a basic role-playing game."
        super().__init__(command_prefix=["~", "%", "./"], description=description)
        super().__init__(command_prefix=["~", "%", "./", "."], description=description)
        self.default_nick = "Miniscape"
        self.add_command(self.load)
        self.remove_command('help')
        self.initialize_managers()

        for extension in extensions_generator():
            try:
                self.load_extension(extension)
                print(f"Successfully loaded extension {extension}.")
            except Exception as e:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

        self.setup_logging()

    @staticmethod
    def setup_logging():
        root = logging.getLogger()
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = jsonlogger.JsonFormatter()
        ch.setFormatter(formatter)
        root.addHandler(ch)
        logging.getLogger(__name__).info("Logging initialized")
        pass

    def initialize_managers(self):
        # TODO(mitch): reenable trading?
        # self.trade_manager = tm.TradeManager()
        pass

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
                                       'https://github.com/coizioc/miniscape/blob/master/README.md')
        await self.process_commands(message)

    async def on_command_error(self, ctx, *args, **kwargs):
        exc = args[0]
        if type(exc) == CheckFailure:
            return
        raise args[0]

    @asyncio.coroutine
    def process_commands(self, message):
        ctx = yield from self.get_context(message, cls=MiniscapeBotContext)
        try:
            if ctx.command is not None:
                log_str = f'{ctx.author.name} ({ctx.author.id}) issued command ' \
                          f'"{ctx.message.clean_content}" ' \
                          f'on guild {ctx.message.guild} ({ctx.message.guild.id})'
                logging.getLogger(__name__).info(log_str)
        except Exception as e:
            pass
        yield from self.invoke(ctx)

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


class MiniscapeBotContext(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.user_object = User.objects.get(id=self.author.id)
        except ObjectDoesNotExist:
            self.user_object = User(id=self.author.id,
                                    name=self.author.name + '#' + self.author.discriminator,
                                    nick=self.author.nick if self.author.nick is not None else '')
            self.user_object.save()
            return

        # Update our user's name/nick if they differ or don't exist
        # (if they don't exist they == '' or == None)
        name_match = self.user_object.name == (self.author.name + '#' + self.author.discriminator)
        nick_match = True
        if self.author.nick:
            nick_match = self.author.nick == self.user_object.nick

        if not name_match or not nick_match:
            self.user_object.nick = self.author.nick if self.author.nick is not None else ''
            self.user_object.name = self.author.name + '#' + self.author.discriminator
            self.user_object.save()

