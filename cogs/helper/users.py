import datetime
import os
import shutil
import time
import ujson
from collections import Counter

from cogs.helper import items
from cogs.helper import prayer
from cogs.helper import quests
from config import USER_DIRECTORY, BACKUP_DIRECTORY, XP_FILE, ARMOUR_SLOTS_FILE

XP = {}
with open(XP_FILE, 'r') as f:
    for line in f.read().splitlines():
        line_split = line.split(';')
        XP[line_split[0]] = int(line_split[1])

SLOTS = {}
with open(ARMOUR_SLOTS_FILE, 'r') as f:
    for line in f.read().splitlines()[1:]:
        line_split = line.split(';')
        SLOTS[line_split[0]] = line_split[1]

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

CHARACTER_HEADER = f'__**:crossed_swords: $NAME :crossed_swords:**__\n'


def add_counter(userid, value, number, key=MONSTERS_KEY):
    """Adds a Counter to another Counter in a user's account."""
    new_counts = Counter({value: int(number)})
    try:
        with open(f'{USER_DIRECTORY}{userid}.json', 'r') as f:
            userjson = ujson.load(f)
        counts = Counter(userjson[key])
        total_counts = counts + new_counts
        userjson[key] = total_counts
    except FileNotFoundError:
        userjson = DEFAULT_ACCOUNT
        userjson[MONSTERS_KEY] = new_counts
    with open(f'{USER_DIRECTORY}{userid}.json', 'w+') as f:
        ujson.dump(userjson, f)


def backup():
    """Backs up the user files."""
    current_time = int(time.time())
    destination = f'{BACKUP_DIRECTORY}{current_time}/'
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    for file in os.listdir(USER_DIRECTORY):
        shutil.copy(f'{USER_DIRECTORY}{file}', destination)


def calc_xp_to_level(userid, skill, level):
    """Calculates the xp needed to get to a level."""
    if skill not in SKILLS:
        return f'{skill} is not a skill.'

    if level is None:
        level = get_level(userid, key=skill) + 1

    if level > 99:
        return f'You have already attained the maximum level in this skill.'

    current_xp = read_user(userid, key=skill)
    for xp_value in XP.keys():
        if XP[xp_value] == level:
            xp_needed = int(xp_value) - current_xp
            break
    else:
        raise KeyError
    xp_formatted = '{:,}'.format(xp_needed)

    out = f'You need {xp_formatted} xp to get level {level} in {skill}.'
    return out


def clear_inventory(userid, under=None):
    """Removes all items (with value) in an account's inventory."""
    if under is not None:
        max_sell = int(under)
    else:
        max_sell = 2147483647
    inventory = read_user(userid)
    locked_items = read_user(userid, key=LOCKED_ITEMS_KEY)
    for itemid in inventory.keys():
        value = items.get_attr(itemid, key=items.VALUE_KEY)
        if inventory[itemid] > 0 and 0 < value < max_sell and itemid not in locked_items:
            inventory[itemid] = 0
    update_user(userid, inventory, key=ITEMS_KEY)


def eat(userid, item):
    if item == 'none' or item == 'nothing':
        update_user(userid, '-1', key=FOOD_KEY)
        return f'You are now eating nothing.'
    try:
        itemid = items.find_by_name(item)
    except KeyError:
        return f'{item} does not exist.'
    item_name = items.get_attr(itemid)
    edible = items.get_attr(itemid, key=items.EAT_KEY)
    if edible > 0:
        update_user(userid, itemid, key=FOOD_KEY)
        return f'You are now eating {items.add_plural(0, itemid)}!'
    else:
        return f'You cannot eat {item_name}.'


def equip_item(userid, item):
    """Takes an item out of a user's inventory and places it into their equipment."""
    try:
        itemid = items.find_by_name(item)
    except KeyError:
        return f'Error: {item} does not exist.'
    item_level = items.get_attr(itemid, key=items.LEVEL_KEY)
    user_cb_level = xp_to_level(read_user(userid, key=COMBAT_XP_KEY))

    if user_cb_level >= item_level:
        item_name = items.get_attr(itemid)
        if item_in_inventory(userid, itemid):
            slot = str(items.get_attr(itemid, key=items.SLOT_KEY))
            if int(slot) > 0:
                if items.get_attr(itemid, key=items.MAX_KEY):
                    total = get_total_level(userid)
                    if total != 99 * len(SKILLS):
                        return f"You cannot equip this item since you do not have {99 * len(SKILLS)} skill total."
                equipment = read_user(userid, key=EQUIPMENT_KEY)
                if slot not in equipment.keys() or equipment[slot] == -1:
                    equipment[slot] = itemid
                else:
                    update_inventory(userid, [equipment[slot]])
                    equipment[slot] = itemid
                update_inventory(userid, [itemid], remove=True)
                update_user(userid, equipment, EQUIPMENT_KEY)
                return f'{item_name} equipped to {SLOTS[slot]}!'
            else:
                return f'Error: {item_name} cannot be equipped.'
        else:
            return f'Error: {item_name} not in inventory.'
    else:
        return f'Error: Insufficient level to equip item ({item_level}). Your current combat level is {user_cb_level}.'


def unequip_item(userid, item, isitemid=False):
    """Takes an item out of a user's equipment and places it into their inventory."""
    if not isitemid:
        try:
            itemid = items.find_by_name(item)
        except KeyError:
            return f'Error: {item} does not exist.'
    else:
        itemid=item
    
    item_name = items.get_attr(itemid)
    equipment = read_user(userid, key=EQUIPMENT_KEY)
    if itemid in equipment.values():
        slot = str(items.get_attr(itemid, key=items.SLOT_KEY))
        if int(slot) > 0:
            equipment = read_user(userid, key=EQUIPMENT_KEY)
            if equipment[slot] == -1:
                return f'{item_name} is not equipped in {SLOTS[str(slot)]}.'
            update_inventory(userid, [itemid])
            equipment[slot] = -1
            update_user(userid, equipment, EQUIPMENT_KEY)
            return f'{item_name} unequipped from {SLOTS[str(slot)]}!'
        else:
            return f'Error: {item_name} cannot be unequipped.'
    else:
        return f'You do not have {item_name} equipped.'


def count_item_in_inventory(userid, itemid):
    """Gets the number of a given item from a user's inventory."""
    inventory = read_user(userid, key=ITEMS_KEY)
    try:
        number = int(inventory[str(itemid)])
    except KeyError:
        number = 0
    return number


def get_total_level(userid):
    """Gets the total level of a user."""
    total_level = 0
    for skill in SKILLS:
        total_level += get_level(userid, key=skill)
    return total_level


def get_values_by_account(key=ITEMS_KEY):
    """Gets a certain value from all user's accounts and sorts them in descending order."""
    leaderboard = []
    for userfile in os.listdir(f'{USER_DIRECTORY}'):
        userid = userfile[:-5]

        if key == ITEMS_KEY:
            value = get_value_of_inventory(userid)
        elif key == QUESTS_KEY:
            value = len(get_completed_quests(userid))
        elif key == 'total':
            value = get_total_level(userid)
        else:
            value = read_user(userid, key=key)

        if value > 0:
            leaderboard.append((int(userid), int(value)))
    return sorted(leaderboard, key=lambda x: x[1], reverse=True)


def get_completed_quests(userid):
    hex_number = int(str(read_user(userid, key=QUESTS_KEY))[2:], 16)
    binary_number = str(bin(hex_number))[2:]
    completed_quests = []
    for bit in range(len(binary_number)):
        if binary_number[bit] == '1':
            completed_quests.append(len(binary_number) - bit)
    return completed_quests


def get_equipment_stats(equipment, userid=None):
    """Gets the total combat stats for the current equipment worn by a user."""
    damage = 0
    accuracy = 0
    armour = 0
    prayer_bonus = 0
    for itemid in equipment.values():
        try:
            damage += items.get_attr(itemid, key=items.DAMAGE_KEY)
            accuracy += items.get_attr(itemid, key=items.ACCURACY_KEY)
            armour += items.get_attr(itemid, key=items.ARMOUR_KEY)
            prayer_bonus += items.get_attr(itemid, key=items.PRAYER_KEY)
        except KeyError:
            pass

    if userid is not None:
        user_prayer = read_user(userid, key=PRAY_KEY)
        damage *= prayer.get_attr(user_prayer, key=prayer.DAMAGE_KEY) / 100
        accuracy *= prayer.get_attr(user_prayer, key=prayer.ACCURACY_KEY) / 100
        armour *= prayer.get_attr(user_prayer, key=prayer.ARMOUR_KEY) / 100

    return damage, accuracy, armour, prayer_bonus


def get_level(userid, key):
    """Gets a user's skill level from their userid."""
    xp = read_user(userid, key=key)
    return xp_to_level(xp)


def get_value_of_inventory(userid, inventory=None, under=None, add_locked=False):
    """Gets the total value of a user's inventory."""
    if inventory is None:
        inventory = read_user(userid)
    if under is not None:
        max_value = int(under)
    else:
        max_value = 999999999999

    total_value = 0
    locked_items = set(read_user(userid, key=LOCKED_ITEMS_KEY))
    for item in list(inventory.keys()):
        value = items.get_attr(item, key=items.VALUE_KEY)
        if value < max_value:
            if item not in locked_items or add_locked:
                total_value += int(inventory[item]) * value
    return total_value


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


def lock_item(userid, item):
    """Locks an item from being sold accidentally."""
    try:
        itemid = items.find_by_name(item)
    except KeyError:
        return f'No item with name {item} found.'

    item_name = items.get_attr(itemid)
    locked_items = read_user(userid, key=LOCKED_ITEMS_KEY)
    if itemid in locked_items:
        return f'{item_name} is already locked.'
    locked_items.append(itemid)
    update_user(userid, locked_items, key=LOCKED_ITEMS_KEY)

    return f'{item_name} has been locked!'


def unlock_item(userid, item):
    """Unlocks an item, allowing it to be sold again."""
    try:
        itemid = items.find_by_name(item)
    except KeyError:
        return f'No item with name {item} found.'

    item_name = items.get_attr(itemid)
    locked_items = read_user(userid, key=LOCKED_ITEMS_KEY)
    if itemid not in locked_items:
        return f'{item_name} is already unlocked.'
    locked_items.remove(itemid)
    update_user(userid, locked_items, key=LOCKED_ITEMS_KEY)

    return f'{item_name} has been unlocked!'


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


def print_account(userid, nickname, printequipment=True):
    """Writes a string showing basic user information."""
    out = f"{CHARACTER_HEADER.replace('$NAME', nickname.upper())}"

    for skill in SKILLS:
        xp_formatted = '{:,}'.format(read_user(userid, key=skill))
        level = get_level(userid, skill)
        out += f'**{skill.title()} Level**: {level} *({xp_formatted} xp)*\n'

    total = get_total_level(userid)
    out += f'**Skill Total**: {total}/{len(SKILLS) * 99}\n\n'
    out += f'**Quests Completed**: {len(get_completed_quests(userid))}/{len(quests.QUESTS.keys())}\n\n'

    if total < 99 * len(SKILLS):
        for itemid in read_user(userid, key=EQUIPMENT_KEY).values():
            if itemid != -1:
                if items.get_attr(itemid, key=items.MAX_KEY):
                    unequip_item(userid, itemid, isitemid=True)
    if printequipment:
        out += print_equipment(userid)

    return out


def print_equipment(userid, name=None, with_header=False):
    """Writes a string showing the stats of a user's equipment."""
    if with_header and name is not None:
        out = f"{CHARACTER_HEADER.replace('$NAME', name.upper())}"
    else:
        out = ''
    equipment = read_user(userid, key=EQUIPMENT_KEY)
    damage, accuracy, armour, prayer = get_equipment_stats(equipment)
    out += f'**Damage**: {damage}\n' \
           f'**Accuracy**: {accuracy}\n' \
           f'**Armour**: {armour}\n' \
           f'**Prayer Bonus**: {prayer}\n\n'
    for slot in equipment.keys():
        out += f'**{SLOTS[str(slot)].title()}**: '
        if int(equipment[slot]) > -1:
            out += f'{items.get_attr(equipment[slot])} ' \
                   f'*(dam: {items.get_attr(equipment[slot], key=items.DAMAGE_KEY)}, ' \
                   f'acc: {items.get_attr(equipment[slot], key=items.ACCURACY_KEY)}, ' \
                   f'arm: {items.get_attr(equipment[slot], key=items.ARMOUR_KEY)}, ' \
                   f'pray: {items.get_attr(equipment[slot], key=items.PRAYER_KEY)})*\n'
        else:
            out += f'none *(dam: 0, acc: 0, arm: 0, pray: 0)*\n'
    return out


def print_inventory(person, search):
    """Prints a list of a user's inventory into discord message-sized chunks."""
    inventory = read_user(person.id)
    if person.nick is None:
        name = person.name
    else:
        name = person.nick
    header = f":moneybag: __**{name.upper()}'S INVENTORY**__ :moneybag:\n"
    messages = []
    out = header

    locked_items = read_user(person.id, key=LOCKED_ITEMS_KEY)
    sorted_items = []
    for itemid in inventory.keys():
        sorted_items.append((items.get_attr(itemid), itemid))
    for name, itemid in sorted(sorted_items, key=lambda tup: tup[0]):
        # name = items.get_attr(itemid)
        if search != '':
            if search not in name.lower():
                continue
        value = items.get_attr(itemid, key=items.VALUE_KEY)
        value_formatted = '{:,}'.format(value)
        item_total_value = int(inventory[itemid]) * value
        item_total_value_formatted = '{:,}'.format(item_total_value)
        if inventory[itemid] > 0:
            out += f'**{items.get_attr(itemid).title()} '
            if itemid in locked_items:
                out += f'(:lock:)'
            out += f'**: {inventory[itemid]}. *(value: {item_total_value_formatted}, {value_formatted} ea.)*\n'
        if len(out) > 1800:
            messages.append(out)
            out = header
    total_value = '{:,}'.format(get_value_of_inventory(person.id, add_locked=True))
    out += f'*Total value: {total_value}*\n'
    messages.append(out)
    return messages


def print_pets(userid):
    """Prints a formatted list of pets a user has."""
    pet_ids = [x for x in items.ITEMS.keys() if items.get_attr(x, key=items.PET_KEY)]
    pet_names = {} # [items.get_attr(x) for x in pet_ids]
    for petid in pet_ids:
        pet_names[items.get_attr(petid)] = petid
    messages = []
    pets_header = f':cat: __**PETS**__ :dog:\n'
    out = pets_header
    pet_count = 0
    for pet_name in sorted(pet_names):
        petid = pet_names[pet_name]
        if item_in_inventory(userid, petid, 1):
            out += f"**{pet_name.title()}**\n"
            pet_count += 1
        else:
            out += f'{pet_name.title()}\n'
        if len(out) > 1900:
            messages.append(out)
            out = pets_header
    out += f'{pet_count}/{len(pet_ids)}'
    messages.append(out)
    return messages


def read_user_multi(*args, **kwargs):
    """Reads the value of the same key across multiple users"""
    return [read_user(u, key=kwargs['key']) for u in args]


def read_user(userid, key=ITEMS_KEY):
    """Reads the value of a key within a user's account."""
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


def remove_potion(userid):
    """Removes a potion from a player's equipment."""
    equipment = read_user(userid, key=EQUIPMENT_KEY)
    equipment['15'] = -1
    update_user(userid, equipment, key=EQUIPMENT_KEY)


def reset_account(userid):
    """Sets a user's keys to the DEFAULT_ACCOUNT."""
    userjson = DEFAULT_ACCOUNT
    with open(f'{USER_DIRECTORY}{userid}.json', 'w+') as f:
        ujson.dump(userjson, f)


def reset_dailies():
    """Resets the completion of all users' dailies."""
    for userid in os.listdir(USER_DIRECTORY):
        if userid[:-4] == 'json':
            userid = userid[:-5] 
            update_user(userid, False, key=VIS_KEY)
            update_user(userid, 0, key=VIS_ATTEMPTS_KEY)
            update_user(userid, False, key=REAPER_KEY)


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


def xp_to_level(xp):
    """Converts a  user's xp into its equivalent level based on an XP table."""
    for level_xp in XP:
        if int(level_xp) > xp:
            return int(XP[level_xp]) - 1
    else:
        return 99
