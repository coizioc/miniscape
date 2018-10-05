import ujson

from config import BANLIST_JSON

try:
    with open(BANLIST_JSON, 'r') as f:
        BANLIST = ujson.load(f)
except FileNotFoundError:
    BANLIST = {}
    with open(BANLIST_JSON, 'w+') as f:
        ujson.dump(BANLIST)


def add_ban(userid, time=-1):
    BANLIST[userid] = time
    write_banlist(BANLIST)


def remove_ban(userid):
    try:
        BANLIST.pop(userid)
        write_banlist(BANLIST)
    except ValueError:
        pass


def write_banlist(banlist):
    with open(BANLIST_JSON, 'w+') as f:
        ujson.dump(banlist)
