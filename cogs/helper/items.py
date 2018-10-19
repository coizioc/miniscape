"""This module contains methods that handle items and their attributes."""
import random
import ujson
from collections import Counter

from cogs.helper import clues
from cogs.helper import monsters as mon
from cogs.helper import prayer
from cogs.helper import users
from config import ITEM_JSON, SHOP_FILE, ITEMS_EMOJI

with open(ITEM_JSON, 'r', encoding='utf-8-sig') as f:
    ITEMS = ujson.load(f)

NAME_KEY = 'name'           # Name of the item
PLURAL_KEY = 'plural'       # string containing how to pluralise an item's name.
NICK_KEY = 'nick'           # list of nicknames for an item.
VALUE_KEY = 'value'         # High alch value of the item
DAMAGE_KEY = 'damage'       # Damage stat of the item
ACCURACY_KEY = 'accuracy'   # Accuracy stat of the item
ARMOUR_KEY = 'armour'       # Armour stat of the item
PRAYER_KEY = 'prayer'       # Prayer drain bonus of the item.
SLOT_KEY = 'slot'           # Slot item can be equipped
AFFINITY_KEY = 'aff'        # Item affinity, 0:Melee, 1:Range, 2:Magic
LEVEL_KEY = 'level'         # Level item can be equipped/gathered
XP_KEY = 'xp'               # xp gained for gathering/crafting the item.
QUEST_KEY = 'quest req'     # quest required to gather an item.
TALISMAN_KEY = 'talisman'   # Itemid of the talisman needed in inventory to craft rune.
POUCH_KEY = 'pouch'         # Int representing how many extra rune essence can be held per trip.
GATHER_KEY = 'gather'       # Boolean whether item can be gathered.
TREE_KEY = 'tree'           # Boolean whether gatherable is a tree.
ROCK_KEY = 'rock'           # Boolean whether gatherable is a rock.
FISH_KEY = 'fish'           # Boolean whether gatherable is a fish.
POT_KEY = 'potion'          # Boolean whether consumable is a potion.
RUNE_KEY = 'rune'           # Boolean whether item is a rune.
COOK_KEY = 'cook'           # Boolean whether item can be cooked.
BURY_KEY = 'bury'           # Boolean whether item can be buried.
MAX_KEY = 'max'		        # Boolean whether max skill total is a req to wear item.
PET_KEY = 'pet'             # Boolean whether item is a pet.
EAT_KEY = 'eat'             # Int representing chance improvement by item when set as food.
LUCK_KEY = 'luck'           # float representing factor of luck enhancement
DEFAULT_ITEM = {NAME_KEY: 'unknown item',
                PLURAL_KEY: 's',
                NICK_KEY: [],
                VALUE_KEY: 0,
                DAMAGE_KEY: 0,
                ACCURACY_KEY: 0,
                ARMOUR_KEY: 0,
                PRAYER_KEY: 0,
                SLOT_KEY: 0,
                AFFINITY_KEY: 0,
                LEVEL_KEY: 1,
                XP_KEY: 1,
                QUEST_KEY: 0,
                TALISMAN_KEY: -1,
                POUCH_KEY: 0,
                GATHER_KEY: False,
                TREE_KEY: False,
                ROCK_KEY: False,
                FISH_KEY: False,
                POT_KEY: False,
                COOK_KEY: False,
                BURY_KEY: False,
                RUNE_KEY: False,
                MAX_KEY: False,
                PET_KEY: False,
                EAT_KEY: 0,
                LUCK_KEY: 1
                }

SHOP_HEADER = f'{ITEMS_EMOJI} __**SHOP**__ {ITEMS_EMOJI}\n'


def add_plural(number, itemid, with_zero=False):
    if int(number) > 0:
        out = f'{number} {get_attr(itemid)}'
    else:
        out = f'{get_attr(itemid)}'
    if int(number) != 1:
        suffix = get_attr(itemid, key=PLURAL_KEY)
        for c in suffix:
            out = out[:-1] if c == '_' else out + c
    return out




def claim(userid, itemname, number):
    try:
        itemid = find_by_name(itemname)
    except KeyError:
        return f"Error: {itemname} is not an item."

    if not users.item_in_inventory(userid, itemid, number):
        return f'You do not have {add_plural(number, itemid)} in your inventory.'

    out = ':moneybag: __**CLAIM**__ :moneybag:\n'
    if itemid == "402":
        out += 'You have received:\n'
        gems = {
            25: 4,
            26: 16,
            27: 64,
            28: 128,
            463: 256,
            465: 512
        }
        loot = []
        for _ in range(number):
            while True:
                gem_type = random.sample(gems.keys(), 1)[0]
                if random.randint(1, gems[gem_type]) == 1:
                    loot.append(gem_type)
                    break
        users.update_inventory(userid, loot)
        loot_counter = Counter(loot)
        for gemid in loot_counter.keys():
            out += f'{add_plural(loot_counter[gemid], gemid)}\n'
        out += f'from your {add_plural(number, itemid)}.'
        users.update_inventory(userid, number * [itemid], remove=True)
    elif itemid == "370":
        xp_per_effigy = 30000
        skills = Counter()
        for _ in range(number):
            skill = random.sample(users.SKILLS, 1)[0]
            skills[skill] += 1
        users.update_inventory(userid, number * ['371'])
        users.update_inventory(userid, number * [itemid], remove=True)
        out += f"You have received the following xp from your {add_plural(number, '370')}!\n"
        for skill in skills.keys():
            xp_gained = skills[skill] * xp_per_effigy
            users.update_user(userid, xp_gained, key=skill)
            xp_gained_formatted = '{:,}'.format(xp_gained)
            out += f'{xp_gained_formatted} {skill} xp\n'
    else:
        out += f'{get_attr(itemid)} is not claimable.'
    return out







def find_by_name(name):
    """Finds a item's ID from its name."""
    name = name.lower()
    for itemid in list(ITEMS.keys()):
        if name == ITEMS[itemid][NAME_KEY]:
            return itemid
        if name == add_plural(0, itemid):
            return itemid
        if any([name == nick for nick in get_attr(itemid, key=NICK_KEY)]):
            return itemid
    else:
        raise KeyError


def get_attr(itemid, key=NAME_KEY):
    """Gets an item's attribute from its id."""
    itemid = str(itemid)
    if itemid in set(ITEMS.keys()):
        try:
            return ITEMS[itemid][key]
        except KeyError:
            ITEMS[itemid][key] = DEFAULT_ITEM[key]
            return ITEMS[itemid][key]
    else:
        raise KeyError


def get_luck_factor(userid):
    """Gets the luck factor of a user."""
    equipment = users.read_user(userid, key=users.EQUIPMENT_KEY)
    luck_factor = 1
    for itemid in equipment.values():
        if int(itemid) > 0:
            item_luck = get_attr(itemid, key=LUCK_KEY)
            if item_luck > luck_factor:
                luck_factor = item_luck

    user_prayer = users.read_user(userid, key=users.PRAY_KEY)
    if user_prayer != -1:
        prayer_factor = prayer.get_attr(user_prayer, key=prayer.FACTOR_KEY)
        if prayer_factor > luck_factor:
            luck_factor = prayer_factor
    return luck_factor


def get_quest_shop_items(questid):
    shop = open_shop()
    quest_items = []
    for itemid in shop.keys():
        if shop[itemid] == questid:
            quest_items.append(itemid)
    return quest_items


def get_quest_items(questid):
    quest_item = []
    for itemid in ITEMS.keys():
        if get_attr(itemid, key=QUEST_KEY) == questid:
            quest_item.append(quest_item)
    return quest_item


def is_tradable(itemid):
    if get_attr(itemid, key=VALUE_KEY) < 1 or itemid in {'384', '267', '291'}:
        return False
    return True






