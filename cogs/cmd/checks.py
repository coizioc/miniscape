from cogs.cmd import channel_permissions as cp
from discord.ext import commands


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
