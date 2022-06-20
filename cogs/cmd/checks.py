from cogs.cmd import channel_permissions as cp
from discord.ext import commands

ADMINS = [
    "293219528450637824",  # Coiz
    "116380350296358914",  # Fury
    "147501762566291457",  # Cactuss
    "132049789461200897",  # Bill
]

ADMIN_CHANNELS = [
    "988305756191338556",  # Miniscape #admin-commands
    "578769058560737281",  # Miniscape dev #mitch-testing
]

def can_post():
    def predicate(ctx: commands.Context):
        guildid = ctx.guild.id
        channelid = ctx.channel.id
        guild_perms = cp.get_guild(guildid)
        try:
            for blacklist_channel in guild_perms[cp.BLACKLIST_KEY]:
                if channelid == blacklist_channel:
                    return False
        except KeyError:
            pass

        if cp.WHITELIST_KEY in guild_perms.keys():
            if guild_perms[cp.WHITELIST_KEY]:
                try:
                    for whitelist_channel in guild_perms[cp.WHITELIST_KEY]:
                        if channelid == whitelist_channel:
                            break
                    else:
                        return False
                except KeyError:
                    pass
        return True

    return commands.check(predicate)


def is_admin():
    def predicate(ctx: commands.Context):
        user = ctx.author.id
        ret = str(user) in ADMINS
        return ret

    return commands.check(predicate)


def is_in_admin_channel():
    def predicate(ctx: commands.Context):
        channel = ctx.channel.id
        ret = str(channel) in ADMIN_CHANNELS
        return ret

    return commands.check(predicate)
