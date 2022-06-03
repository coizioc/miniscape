import config
import string
from enum import Enum, auto
from miniscape.models import Item, User, Quest


class Headers(Enum):
    TOTAL = auto()
    GOLD = auto()
    SLAYER = auto()
    COMBAT = auto()
    GATHER = auto()
    ARTISAN = auto()
    COOK = auto()
    PRAY = auto()
    RC = auto()
    QUESTS = auto()


TITLES = {
    Headers.TOTAL: 'total level',
    Headers.GOLD: 'gold',
    Headers.SLAYER: 'slayer',
    Headers.COMBAT: 'combat',
    Headers.GATHER: 'gather',
    Headers.ARTISAN: 'artisan',
    Headers.COOK: 'cooking',
    Headers.PRAY: 'prayer',
    Headers.RC: 'runecrafting',
    Headers.QUESTS: 'quest points'
}

EMOJI = {
    Headers.TOTAL: config.TOTAL_LEVEL_EMOJI,
    Headers.GOLD: config.ITEMS_EMOJI,
    Headers.SLAYER: config.SLAYER_EMOJI,
    Headers.COMBAT: config.COMBAT_EMOJI,
    Headers.GATHER: config.GATHER_EMOJI,
    Headers.ARTISAN: config.ARTISAN_EMOJI,
    Headers.COOK: config.COOK_EMOJI,
    Headers.PRAY: config.PRAY_EMOJI,
    Headers.RC: config.RC_EMOJI,
    Headers.QUESTS: config.QUEST_EMOJI
}


def lb_total(name):
    users = []
    lb = list(User.objects.all())
    for user in lb:
        this_user = {'name': user.nick if user.nick else user.plain_name,
                     'primary': user.total_level,
                     'secondary': user.total_xp}
        users.append(this_user)
    lower, upper = get_leaderboard_range(name, lb)
    return sorted(users, key=lambda x: x['secondary'], reverse=True)[lower:upper]


def lb_gold(name):
    users = []
    coin_itemid = Item.objects.get(name="coins")
    lb = list(User.objects.all())
    for user in lb:
        this_user = {'name': user.nick if user.nick else user.plain_name,
                     'primary': user.get_item_by_item(coin_itemid)[0].amount if user.get_item_by_item(
                         coin_itemid) else 0}
        users.append(this_user)
    lower, upper = get_leaderboard_range(name, lb)
    return sorted(users, key=lambda x: x['primary'], reverse=True)[lower:upper]


def lb_slayer(name):
    return lb_field(name, 'slayer')


def lb_combat(name):
    return lb_field(name, 'combat')


def lb_gather(name):
    return lb_field(name, 'gather')


def lb_artisan(name):
    return lb_field(name, 'artisan')


def lb_cook(name):
    return lb_field(name, 'cook')


def lb_pray(name):
    return lb_field(name, 'prayer')


def lb_rc(name):
    return lb_field(name, 'rc')


def lb_quests(name):
    users = []
    lb = list(User.objects.all())
    for user in lb:
        this_user = {'name': user.nick if user.nick else user.plain_name,
                     'primary': user.num_quests_complete}
        users.append(this_user)
    lower, upper = get_leaderboard_range(name, lb)
    return sorted(users, key=lambda x: x['primary'], reverse=True)[lower:upper]


def lb_field(name, field):
    xp_attr = field + "_xp"
    lvl_attr = field + "_level"
    users = []
    lb = User.objects.order_by('-' + xp_attr)
    lower, upper = get_leaderboard_range(name, lb)
    for user in lb[lower:upper]:
        this_user = {'name': user.nick if user.nick else user.plain_name,
                     'primary': getattr(user, lvl_attr),
                     'secondary': getattr(user, xp_attr)}
        users.append(this_user)
    return users


LEADERBOARDS = {
    Headers.TOTAL: lb_total,
    Headers.GOLD: lb_gold,
    Headers.SLAYER: lb_slayer,
    Headers.COMBAT: lb_combat,
    Headers.GATHER: lb_gather,
    Headers.ARTISAN: lb_artisan,
    Headers.COOK: lb_cook,
    Headers.PRAY: lb_pray,
    Headers.RC: lb_rc,
    Headers.QUESTS: lb_quests
}

PAGE_LENGTH = 10
LEADERBOARD_HEADER = f'$EMOJI __**$KEY LEADERBOARD**__ $EMOJI\n'


def get_leaderboard(key, name):
    """Returns a message containing a leaderboard with the respective key."""

    out = LEADERBOARD_HEADER.replace("$KEY", TITLES[key].upper()).replace("$EMOJI", EMOJI[key])
    for user in LEADERBOARDS[key](name):
        name = user['name']
        primary = user['primary']
        try:
            secondary = user['secondary']
        except KeyError:
            secondary = -1

        primary_formatted = '{:,}'.format(primary)
        out += f'**{string.capwords(name)}**: {primary_formatted}'
        if secondary != -1:
            secondary_formatted = '{:,}'.format(secondary)
            out += f' *({secondary_formatted} xp)*\n'
        elif key == Headers.GOLD:
            out += f' gp\n'
        else:
            out += f'/{Quest.objects.count()} quests\n'
    return out


def get_leaderboard_range(name, leaderboard):
    """Gets the lower and upper bounds of a leaderboard and returns them as a tuple."""
    if name is None:
        lb_range = (0, PAGE_LENGTH)
    elif name == 'bottom':
        lb_range = (leaderboard.count() - PAGE_LENGTH, leaderboard.count())
    else:
        lb_len = leaderboard.count()
        name_index = leaderboard.filter(name__startswith=name)
        if name_index < 5:
            lower = 0
            upper = 10
        else:
            lower = name_index - 5
            upper = name_index + 5
        if name_index + 5 > lb_len:
            upper = lb_len
            lower = lb_len - 10
        lb_range = (lower, upper)
    return lb_range
