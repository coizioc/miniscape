from collections import Counter

import ujson

import config
from config import USER_DIRECTORY

IRONMAN_KEY = 'ironman'         # User's ironman status, stored as a boolean.
ITEMS_KEY = 'items'             # User's inventory, stored as a Counter.
LOCKED_ITEMS_KEY = 'locked'     # Items locked in user's inventory, stored as a list of itemids.
MONSTERS_KEY = 'monsters'       # Count of monsters user has killed, stored as a Counter.
CLUES_KEY = 'clues'             # Count of clues user has completed, stored as a Counter.
EQUIPMENT_KEY = 'equip'         # User's equipment, stored as a dicr.
COMBAT_XP_KEY = 'combat'        # User's combat xp, stored as an int.
SLAYER_XP_KEY = 'slayer'        # User's slayer xp, stored as an int.
GATHER_XP_KEY = 'gather'        # User's gathering xp, stored as an int.
ARTISAN_XP_KEY = 'artisan'      # User's artisan xp, stored as an int.
COOK_XP_KEY = 'cook'            # User's cooking xp, stored as an int.
PRAY_XP_KEY = 'prayer'          # User's prayer xp, stored as an int.
RC_XP_KEY = 'runecrafting'      # User's runecrafting xp, stored as an int.
REAPER_KEY = 'reaperdone'       # Boolean whether user has completed a reaper task today.
VIS_KEY = 'vis'                 # Boolean whether user has recieved vis wax today.
VIS_ATTEMPTS_KEY = 'visattempts'# User's number of daily vis wax attempts.
FOOD_KEY = 'food'               # User's active food, stored as an int.
PRAY_KEY = 'pray'               # User's current prayer, stored as an int.
QUESTS_KEY = 'quests'           # User's completed quests. Stored as a hexadecimal number whose bits represent
                                # whether a user has completed a quest with that questid.
DEFAULT_ACCOUNT = {IRONMAN_KEY: False,
                   ITEMS_KEY: Counter(),
                   LOCKED_ITEMS_KEY: ["0"],
                   MONSTERS_KEY: Counter(),
                   CLUES_KEY: Counter(),
                   EQUIPMENT_KEY: dict(zip(range(1, 16), 15*[-1])),
                   COMBAT_XP_KEY: 0,
                   SLAYER_XP_KEY: 0,
                   GATHER_XP_KEY: 0,
                   ARTISAN_XP_KEY: 0,
                   COOK_XP_KEY: 0,
                   PRAY_XP_KEY: 0,
                   RC_XP_KEY: 0,
                   FOOD_KEY: -1,
                   PRAY_KEY: -1,
                   REAPER_KEY: False,
                   VIS_KEY: False,
                   VIS_ATTEMPTS_KEY: 0,
                   QUESTS_KEY: "0x0"}   # What's this?

SKILLS = [COMBAT_XP_KEY, SLAYER_XP_KEY, GATHER_XP_KEY, ARTISAN_XP_KEY, COOK_XP_KEY, PRAY_XP_KEY, RC_XP_KEY]

LEADERBOARD_TITLES = {
        ITEMS_KEY: 'gold',
        SLAYER_XP_KEY: 'slayer',
        COMBAT_XP_KEY: 'combat',
        GATHER_XP_KEY: 'gather',
        ARTISAN_XP_KEY: 'artisan',
        COOK_XP_KEY: 'cooking',
        PRAY_XP_KEY: 'prayer',
        RC_XP_KEY: 'runecrafting',
        QUESTS_KEY: 'quest points',
        'total': 'total level'
    }

LEADERBOARD_EMOJI = {
        ITEMS_KEY: config.ITEMS_EMOJI,
        SLAYER_XP_KEY: config.SLAYER_EMOJI,
        COMBAT_XP_KEY: config.COMBAT_EMOJI,
        GATHER_XP_KEY: config.GATHER_EMOJI,
        ARTISAN_XP_KEY: config.ARTISAN_EMOJI,
        COOK_XP_KEY: config.COOK_EMOJI,
        PRAY_XP_KEY: config.PRAY_EMOJI,
        RC_XP_KEY: config.RC_EMOJI,
        QUESTS_KEY: config.QUEST_EMOJI,
        'total': config.TOTAL_LEVEL_EMOJI
    }

LEADERBOARD_QUANTIFIERS = {
        ITEMS_KEY: 'gp',
        SLAYER_XP_KEY: 'xp',
        COMBAT_XP_KEY: 'xp',
        GATHER_XP_KEY: 'xp',
        ARTISAN_XP_KEY: 'xp',
        COOK_XP_KEY: 'xp',
        PRAY_XP_KEY: 'xp',
        RC_XP_KEY: 'xp',
        QUESTS_KEY: 'quest points',
        'total': 'levels'
    }

LEADERBOARD_LENGTH = 10

CHARACTER_HEADER = f'{config.COMBAT_EMOJI} __**$NAME**__ {config.COMBAT_EMOJI}\n'
LEADERBOARD_HEADER = f'$EMOJI __**$KEY LEADERBOARD**__ $EMOJI\n'


def item_in_inventory(userid, item, number=1):
    """Determines whether (a given number of) an item is in a user's inventory."""
    with open(f'{USER_DIRECTORY}{userid}.json', 'r+') as f:
        userjson = ujson.load(f)

    try:
        count = userjson[ITEMS_KEY][str(item)]
        if int(count) >= int(number):
            return True
        else:
            return False
    except KeyError:
        return False


def parse_int(number_as_string):
    """Converts an string into an int if the string represents a valid integer"""
    try:
        if len(number_as_string) > 1:
            int(str(number_as_string)[:-1])
        else:
            if len(number_as_string) == 0:
                raise ValueError
            if len(number_as_string) == 1 and number_as_string.isdigit():
                return int(number_as_string)
            else:
                raise ValueError
    except ValueError:
        raise ValueError
    last_char = str(number_as_string)[-1]
    if last_char.isdigit():
        return int(number_as_string)
    elif last_char == 'k':
        return int(number_as_string[:-1]) * 1000
    elif last_char == 'm':
        return int(number_as_string[:-1]) * 1000000
    elif last_char == 'b':
        return int(number_as_string[:-1]) * 1000000000
    else:
        raise ValueError


def read_user_multi(*args, **kwargs):
    """Reads the value of the same key across multiple users"""
    return [read_user(u, key=kwargs['key']) for u in args]


def read_user(userid, key=ITEMS_KEY):
    """Reads the value of a key within a user's account."""

    if key == ITEMS_KEY:
        ret =  User.objects.get(id=userid).get_inventory()
        return ret
        pass


    try:
        with open(f'{USER_DIRECTORY}{userid}.json', 'r') as f:
            userjson = ujson.load(f)
        return userjson[key]
    except FileNotFoundError:
        userjson = DEFAULT_ACCOUNT
        with open(f'{USER_DIRECTORY}{userid}.json', 'w+') as f:
            ujson.dump(userjson, f)
        return userjson[key]
    except KeyError:
        userjson[key] = DEFAULT_ACCOUNT[key]
        with open(f'{USER_DIRECTORY}{userid}.json', 'w+') as f:
            ujson.dump(userjson, f)
        return userjson[key]


def update_inventory(userid, loot, remove=False):
    """Adds or removes items from a user's inventory."""
    try:
        with open(f'{USER_DIRECTORY}{userid}.json', 'r') as f:
            userjson = ujson.load(f)
        inventory = Counter(userjson[ITEMS_KEY])
        loot = Counter(loot)
        inventory = inventory - loot if remove else inventory + loot
        userjson[ITEMS_KEY] = inventory
    except KeyError:
        raise ValueError
    except FileNotFoundError:
        userjson = DEFAULT_ACCOUNT
        userjson[ITEMS_KEY] = Counter(loot)

    with open(f'{USER_DIRECTORY}{userid}.json', 'w+') as f:
        ujson.dump(userjson, f)


def update_user(userid, value, key=ITEMS_KEY):
    """Changes the value of a key within a user's account."""
    userid = str(userid)
    try:
        with open(f'{USER_DIRECTORY}{userid}.json', 'r') as f:
            userjson = ujson.load(f)
    except FileNotFoundError:
        userjson = DEFAULT_ACCOUNT

    if key in SKILLS:
        current_xp = userjson[key]
        userjson[key] = current_xp + value
    elif key == QUESTS_KEY:
        current_quests = int(str(userjson[key])[2:], 16)
        current_quests = current_quests | 1 << (int(value) - 1)
        userjson[key] = str(hex(current_quests))
    else:
        userjson[key] = value

    with open(f'{USER_DIRECTORY}{userid}.json', 'w+') as f:
        ujson.dump(userjson, f)


