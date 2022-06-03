#! /usr/bin/env/python3
"""Provides a launcher that sets up logging for the bot."""
import logging
import contextlib
import os
from pathlib import Path
from mbot import MiniscapeBot

LOG_PATH = './logs/'
LOG_FILE = 'miniscapebot.log'


@contextlib.contextmanager
def setup_logging():
    """Sets up the bot logging."""
    try:
        # __enter__
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)

        log = logging.getLogger()
        log.setLevel(logging.INFO)

        # Make sure the directory exists
        os.makedirs(LOG_PATH, exist_ok=True)

        # Touch the log file to make sure it exists
        f = Path(os.path.join(LOG_PATH, LOG_FILE))
        f.touch()

        handler = logging.FileHandler(filename=f.as_posix(), encoding='utf-8', mode='w')
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter('[{asctime}] [{levelname:<7}] {name}: {message}', dt_fmt, style='{')
        handler.setFormatter(fmt)
        log.addHandler(handler)

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)


def run_bot():
    """Initializes the logger and the bot class."""
    log = logging.getLogger()

    bot = MiniscapeBot()
    bot.run()


def main():
    """Instantiates the bot using setup_logging as a context."""
    with setup_logging():
        run_bot()


if __name__ == "__main__":
    main()
