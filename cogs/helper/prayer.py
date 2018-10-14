import ujson

from cogs.helper import adventures as adv
from cogs.helper import items, users
from config import PRAYERS_JSON

with open(PRAYERS_JSON, 'r') as f:
    PRAYERS = ujson.load(f)

NAME_KEY = 'name'                       # Name of prayer, stored as a string.
NICK_KEY = 'nick'                       # List of nicknames of prayer.
DESC_KEY = 'description'                # Description of function of prayer.
PRAYER_KEY = 'prayer'                   # Prayer requirement.
DRAIN_KEY = 'drain'                     # Drain rate for prayer.
DAMAGE_KEY = 'damage'                   # Percent damage increase for prayer.
ACCURACY_KEY = 'accuracy'               # Percent accuracy increase for prayer.
ARMOUR_KEY = 'armour'                   # Percent armour increase for prayer.
CHANCE_KEY = 'chance'                   # Percent chance increase for prayer.
FACTOR_KEY = 'factor'                   # Factor multiplier increase for prayer.
KEEP_FACTOR_KEY = 'keepfactorondeath'   # Boolean whether factor can be kept on death.
GATHER_KEY = 'gather'                   # Factor of gather time decrease for prayer.
AFFINITY_KEY = 'aff'                    # Int representing the kinds of monsters the prayer works against.
QUEST_KEY = 'quest'                     # Quest requirement for prayer.

DEFAULT_PRAYER = {
    NAME_KEY: 'unknown prayer',
    NICK_KEY: [],
    DESC_KEY: 'unknown description',
    PRAYER_KEY: 1,
    DRAIN_KEY: 100,
    DAMAGE_KEY: 0,
    ACCURACY_KEY: 0,
    ARMOUR_KEY: 0,
    CHANCE_KEY: 0,
    FACTOR_KEY: 1,
    KEEP_FACTOR_KEY: False,
    GATHER_KEY: 1,
    QUEST_KEY: -1
}





def calc_pray_bonus(userid, userprayer=None):
    if userprayer is None:
        userprayer = users.read_user(userid, key=users.PRAY_KEY)
    player_dam, player_acc, player_arm, player_pray = \
        users.get_equipment_stats(users.read_user(userid, key=users.EQUIPMENT_KEY))
    player_dam *= 1 + get_attr(userprayer, key=DAMAGE_KEY) / 50.0
    player_acc *= 1 + get_attr(userprayer, key=ACCURACY_KEY) / 50.0
    player_arm *= 1 + get_attr(userprayer, key=ARMOUR_KEY) / 50.0
    return player_dam, player_acc, player_arm


def calc_drain_time(userid, prayerid):
    """Calculates the effective drain rate of a prayer."""
    user_equipment = users.read_user(userid, key=users.EQUIPMENT_KEY)
    equipment_prayer = users.get_equipment_stats(user_equipment)[3]
    user_potion = user_equipment['15']
    user_prayer = users.get_level(userid, key=users.PRAY_XP_KEY)
    prayer_drain = get_attr(prayerid, key=DRAIN_KEY)

    if user_potion == '199':
        potion_base = 2
    else:
        potion_base = 1

    base_time = float(36 / prayer_drain)
    effective_time = 60 * user_prayer * base_time * potion_base * (1 + equipment_prayer / 30)
    return effective_time


def find_by_name(name):
    """Finds a prayer's ID from its name."""
    name = name.lower()
    for prayerid in list(PRAYERS.keys()):
        if name == PRAYERS[prayerid][NAME_KEY]:
            return prayerid
        if any([name == nick for nick in get_attr(prayerid, key=NICK_KEY)]):
            return prayerid
    else:
        raise KeyError


def get_attr(prayerid, key=NAME_KEY):
    """Gets an prayer's attribute from its id."""
    prayerid = str(prayerid)
    if prayerid in set(PRAYERS.keys()):
        try:
            return PRAYERS[prayerid][key]
        except KeyError:
            PRAYERS[prayerid][key] = DEFAULT_PRAYER[key]
            return PRAYERS[prayerid][key]
    else:
        raise KeyError


def print_info(prayer):
    """Prints information about a particular prayer"""
    try:
        prayerid = find_by_name(prayer)
    except KeyError:
        return f'{prayer} is not a prayer.'

    out = PRAYER_HEADER
    out += f'**Name**: {get_attr(prayerid).title()}\n'
    aliases = get_attr(prayerid, key=NICK_KEY)
    if len(aliases) > 0:
        out += f"**Aliases**: {', '.join(aliases)}\n"
    out += f'**Prayer**: {get_attr(prayerid, key=PRAYER_KEY)}\n'
    out += f'**Drain Rate**: {get_attr(prayerid, key=DRAIN_KEY)}\n'
    out += f'\n*{get_attr(prayerid, key=DESC_KEY)}*'
    return out


def print_list(userid):
    """Lists the prayers the the user can use."""
    messages = []
    out = PRAYER_HEADER

    prayer_lvl = users.get_level(userid, key=users.PRAY_XP_KEY)
    completed_quests = users.get_completed_quests(userid)

    prayer_list = []
    for prayerid in list(PRAYERS.keys()):
        level = get_attr(prayerid, key=PRAYER_KEY)
        prayer_list.append((level, prayerid))
    for prayer in sorted(prayer_list):
        prayer_quest = get_attr(prayer[1], key=QUEST_KEY)
        if prayer_quest not in completed_quests and prayer_quest != -1:
            continue
        if prayer_lvl >= get_attr(prayer[1], key=PRAYER_KEY):
            out += f'**{get_attr(prayer[1]).title()}** *(level {prayer[0]})*\n'
            if len(out) > 1800:
                messages.append(out)
                out = f'{PRAYER_HEADER}'
    out += 'Type `~prayer info [name]` to get more information about a particular prayer.'
    messages.append(out)
    return messages


def set_prayer(userid, prayer):
    """Sets a user's prayer."""
    if adv.is_on_adventure(userid):
        return 'You cannot change your prayer while on an adventure.'

    try:
        prayerid = find_by_name(prayer)
    except KeyError:
        return f'{prayer} is not a prayer.'

    if get_attr(prayerid, key=QUEST_KEY) not in users.get_completed_quests(userid) and get_attr(prayerid, key=QUEST_KEY) != -1:
        return f'You do not have the required quest to use this prayer.'

    users.update_user(userid, prayerid, key=users.PRAY_KEY)
    out = f'{PRAYER_HEADER}Your prayer has been set to {get_attr(prayerid)}!'
    return out
