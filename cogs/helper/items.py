"""This module contains methods that handle items and their attributes."""
import random
import ujson
from collections import Counter

from cogs.helper import clues
from cogs.helper import monsters as mon
from cogs.helper import prayer
from cogs.helper import users
from config import ITEM_JSON, SHOP_FILE

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
                EAT_KEY: 0,
                LUCK_KEY: 1
                }

SHOP_HEADER = '__**:moneybag: SHOP :moneybag:**__\n'


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


def buy(userid, item, number):
    """Buys (a given amount) of an item and places it in the user's inventory."""
    try:
        itemid = find_by_name(item)
        number = int(number)
    except KeyError:
        return f'Error: {item} is not an item.'
    except ValueError:
        return f'Error: {number} is not a number.'
    item_name = get_attr(itemid)
    if item_in_shop(itemid):
        items = open_shop()
        if int(items[itemid]) in users.get_completed_quests(userid) or int(items[itemid]) == 0:
            value = get_attr(itemid, key=VALUE_KEY)
            cost = 4 * number * value
            if users.item_in_inventory(userid, "0", cost):
                users.update_inventory(userid, [itemid] * number)
                users.update_inventory(userid, (4 * number * value) * ["0"], remove=True)
                value_formatted = '{:,}'.format(4 * value * number)
                return f'{number} {item_name} bought for {value_formatted} coins!'
            else:
                return f'You do not have enough coins to buy this item. ({cost} coins)'
        else:
            return 'Error: You do not have the requirements to buy this item.'
    else:
        return f'Error: {item_name} not in inventory or you do not have at least {number} in your inventory.'


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


def compare(item1, item2):
    """Prints a string comparing the stats of two given items."""
    try:
        item1id = find_by_name(item1)
    except KeyError:
        return f'Error: {item1} does not exist.'
    try:
        item2id = find_by_name(item2)
    except KeyError:
        return f'Error: {item2} does not exist.'

    item1_acc = get_attr(item1id, key=ACCURACY_KEY)
    item1_dam = get_attr(item1id, key=DAMAGE_KEY)
    item1_arm = get_attr(item1id, key=ARMOUR_KEY)
    item1_pra = get_attr(item1id, key=PRAYER_KEY)

    item2_acc = get_attr(item2id, key=ACCURACY_KEY)
    item2_dam = get_attr(item2id, key=DAMAGE_KEY)
    item2_arm = get_attr(item2id, key=ARMOUR_KEY)
    item2_pra = get_attr(item2id, key=PRAYER_KEY)

    out = f':moneybag: __**COMPARE**__ :moneybag:\n'\
          f'**{item1} vs {item2}:**\n\n'\
          f'**Accuracy**: {item1_acc} vs {item2_acc} *({item1_acc - item2_acc})*\n' \
          f'**Damage**: {item1_dam} vs {item2_dam} *({item1_dam - item2_dam})*\n' \
          f'**Armour**: {item1_arm} vs {item2_arm} *({item1_arm - item2_arm})*\n' \
          f'**Prayer Bonus**: {item1_pra} vs {item2_pra} *({item1_pra - item2_pra})*'
    return out


def drink(userid, name):
    try:
        itemid = find_by_name(name)
    except KeyError:
        return f'Error: {name} does not exist.'
    item_name = get_attr(itemid)

    is_pot = get_attr(itemid, key=POT_KEY)
    if is_pot:
        if users.item_in_inventory(userid, itemid):
            users.update_inventory(userid, [itemid], remove=True)
            equipment = users.read_user(userid, key=users.EQUIPMENT_KEY)
            equipment['15'] = str(itemid)
            users.update_user(userid, equipment, key=users.EQUIPMENT_KEY)
        else:
            return f"You do not have any {add_plural(0, itemid)} in your inventory."
    else:
        return f"{item_name} isn't a potion!"

    out = f'You drank the {item_name}! Your stats will be increased for your next adventure.'
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


def item_in_shop(itemid):
    """Checks if an item is in the shop."""
    return str(itemid) in set(open_shop().keys())


def open_shop():
    """Opens the shop file and places the items and quest reqs in a dictionary."""
    with open(SHOP_FILE, 'r') as f:
        lines = f.read().splitlines()
    items = {}
    for line in lines:
        itemid, quest_req = line.split(';')
        items[itemid] = quest_req
    return items


def sell(userid, item, number):
    """Sells (a given amount) of an item from a user's inventory."""
    try:
        itemid = find_by_name(item)
        number = int(number)
    except KeyError:
        return f'Error: {item} is not an item.'
    except ValueError:
        return f'Error: {number} is not a number.'

    item_name = get_attr(itemid)
    if users.item_in_inventory(userid, itemid, number=number):
        value = get_attr(itemid, key=VALUE_KEY)
        users.update_inventory(userid, [itemid] * number, remove=True)
        users.update_inventory(userid, (number * value) * ["0"])
        value_formatted = '{:,}'.format(value * number)
        return f'{number} {item_name} sold for {value_formatted} coins!'
    else:
        return f'Error: {item_name} not in inventory or you do not have at least {number} in your inventory.'


def print_shop(userid):
    """Prints the shop."""
    items = open_shop()

    out = SHOP_HEADER
    messages = []
    for itemid in list(items.keys()):
        if int(items[itemid]) in set(users.get_completed_quests(userid)) or items[itemid] == '0':
            name = get_attr(itemid)
            price = '{:,}'.format(4 * get_attr(itemid, key=VALUE_KEY))
            out += f'**{name.title()}**: {price} coins\n'
        if len(out) > 1800:
            messages.append(out)
            out = SHOP_HEADER
    messages.append(out)
    return messages


def print_stats(item):
    """Prints the stats of an item."""
    try:
        itemid = find_by_name(item)
    except KeyError:
        return f'Error: {item} is not an item.'

    name = get_attr(itemid).title()
    value = '{:,}'.format(get_attr(itemid, key=VALUE_KEY))
    aliases = ', '.join(get_attr(itemid, key=NICK_KEY))
    damage = get_attr(itemid, key=DAMAGE_KEY)
    accuracy = get_attr(itemid, key=ACCURACY_KEY)
    armour = get_attr(itemid, key=ARMOUR_KEY)
    prayer = get_attr(itemid, key=PRAYER_KEY)
    slot = get_attr(itemid, key=SLOT_KEY)
    level = get_attr(itemid, key=LEVEL_KEY)

    out = f'__**:moneybag: ITEMS :moneybag:**__\n'
    out += f'**Name**: {name}\n'
    if len(aliases) > 0:
        out += f'**Aliases**: {aliases}\n'
    out += f'**Value**: {value} gp\n'
    if slot > 0:
        out += f'**Damage**: {damage}\n'
        out += f'**Accuracy**: {accuracy}\n'
        out += f'**Armour**: {armour}\n'
        out += f'**Prayer Bonus**: {prayer}\n'
        out += f'**Slot**: {users.SLOTS[str(slot)].title()}\n'
        out += f'**Combat Requirement**: {level}\n'
    if get_attr(itemid, key=GATHER_KEY):
        xp = get_attr(itemid, key=XP_KEY)
        out += f'**Gather Requirement**: {level}\n'
        out += f'**xp**: {xp}\n'

    out += "\n" + mon.print_item_from_lootable(itemid)
    out += clues.print_item_from_lootable(itemid)
    return out
