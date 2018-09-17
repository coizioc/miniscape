import ujson

from config import CHANNEL_PERMISSIONS_JSON

WHITELIST_KEY = 'white'   # list containing all channels in a guild in which the bot can run commands.
BLACKLIST_KEY = 'black'   # list containing all channels in a guild in which the bot cannot run commands.


def add_channel(guildid, channelid, key):
    """Adds a channel to the file."""
    guildid = str(guildid)
    try:
        perms = get_file()
        guild_perms = perms[str(guildid)]
    except KeyError:
        perms[guildid] = {key: [channelid]}
        write(perms)
        return

    try:
        perms[guildid][key].append(channelid)
    except KeyError:
        perms[guildid][key] = [channelid]

    write(perms)


def get_file():
    """Opens the permissions file, or returns an empty dict if it does not exist."""
    try:
        with open(CHANNEL_PERMISSIONS_JSON, 'r') as f:
            return ujson.load(f)
    except FileNotFoundError:
        with open(CHANNEL_PERMISSIONS_JSON, 'w+') as f:
            ujson.dump({}, f)
        return {}


def get_guild(guildid):
    """Gets the white/blacklist for a guild, or raises a KeyError if it is not found."""
    try:
        return get_file()[str(guildid)]
    except KeyError:
        return {}


def remove_channel(guildid, channelid, key):
    """Removes a channel from the file."""
    guildid = str(guildid)
    try:
        perms = get_file()
        guild_perms = perms[str(guildid)]
    except KeyError:
        raise ValueError

    try:
        perms[guildid][key].remove(channelid)
        write(perms)
    except KeyError:
        raise ValueError
    except ValueError:
        raise ValueError


def write(permissions_dict):
    """Writes the permissions dict to a json file."""
    with open(CHANNEL_PERMISSIONS_JSON, 'w+') as f:
        ujson.dump(permissions_dict, f)
