import random

from cogs.cmd import channel_permissions as cp
from miniscape.models import User


class AmbiguousInputError(Exception):
    """Error raised for input that refers to multiple users"""
    def __init__(self, output):
        self.output = output


def get_member_from_guild(guild_members, username):
    """From a str username and a list of all guild members returns the member
    whose name contains username."""
    username = username.lower()
    if username == 'rand':
        return random.choice(guild_members)
    members = []
    for member in guild_members:
        lower_name = member.name.replace(' ', '').lower()
        if member.nick is not None:
            lower_nick = member.nick.replace(' ', '').lower()
            if username == lower_nick:
                return member
            if username in lower_nick:
                members.append(member)
        elif username == lower_name:
            return member
        elif username in lower_name:
            members.append(member)

    if not members:
        raise NameError(username)
    elif len(members) == 1:
        return members[0]
    else:
        raise AmbiguousInputError([member.name for member in members])


def get_display_name(member):
    """Gets the displayed name of a user."""
    if member.nick is None:
        name = member.name
    else:
        name = member.nick
    if User.objects.get(id=member.id).is_ironman:
        name += ' (IM)'
    return name


def parse_name(guild, username):
    """Gets the username of a user from a string and guild."""
    if '@' in username:
        try:
            return guild.get_member(int(username[3:-1]))
        except:
            raise NameError(username)
    else:
        return get_member_from_guild(guild.members, username)


def has_post_permission(guildid, channelid):
    """Checks whether the bot can post in that channel."""
    # if cp.in_panic():
    #     return channelid == TEST_CHANNEL
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