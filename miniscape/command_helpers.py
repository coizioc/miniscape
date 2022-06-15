import random
import string
from collections import Counter

from miniscape import clue_helpers
from miniscape.models import Item, User, UserInventory, MonsterLoot
from miniscape.itemconsts import SAPPHIRE, EMERALD, RUBY, DIAMOND, LAPIS_LAZULI, QUARTZ, GEM_ROCK,\
    ANCIENT_EFFIGY, OPENED_ANCIENT_EFFIGY, EFFY, CHRISTMAS_CRACKER
import config
from config import ARMOUR_SLOTS_FILE, XP_PER_EFFIGY


PRAYER_HEADER = f':pray: __**PRAYER**__ :pray:\n'


SLOTS = {}
with open(ARMOUR_SLOTS_FILE, 'r') as f:
    for line in f.read().splitlines()[1:]:
        line_split = line.split(';')
        SLOTS[line_split[0]] = line_split[1]


def parse_int(number_as_string):
    """Converts an string into an int if the string represents a valid integer"""
    if type(number_as_string) == tuple:
        number_as_string = number_as_string[0]
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


def parse_number_and_name(args):
    """Parses the number and item name from an arbitrary number of arguments."""
    if len(args) == 0:
        number = None
        name = None
    elif len(args) == 1:
        number = 1
        name = args[0]
    else:
        try:
            number = parse_int(args[0])
            name = ' '.join(args[1:])
        except ValueError:
            number = 1
            name = ' '.join(args)
    return number, name


def parse_number_name_length(args):
    """Parses arguments of the form [number] [name] [length]."""
    if args:
        try:
            number = parse_int(args[0])
            name = ' '.join(args[1:])
            length = None
        except ValueError:
            number = None
            try:
                name = ' '.join(args[:-1])
                length = parse_int(args[-1])
            except ValueError:
                name = ' '.join(args)
                length = None
        return number, name, length
    else:
        return None, None, None


def print_inventory(person, search):
    """Prints a list of a user's inventory into discord message-sized chunks."""
    name = person.nick if person.nick else person.plain_name

    inventory = person.get_inventory(search)

    lock_template = "**%s (:lock:)**: %s. *(value: %s, %s ea)*\n"
    unlock_template = "**%s**: %s. *(value: %s, %s ea)*\n"

    messages = [(lock_template if item.is_locked else unlock_template)
                % (
                    string.capwords(item.item.name),
                    '{:,}'.format(item.amount),
                    '{:,}'.format(item.total_value),
                    '{:,}'.format(item.item.value)
                ) for item in inventory]

    ret = []
    header = f"{config.ITEMS_EMOJI} __**{name.upper()}'S INVENTORY**__ {config.ITEMS_EMOJI}\n"
    out = header
    for message in messages:
        if len(out) + len(message) > 1800:
            ret.append(out)
            out = header
        out = out + message

    # Make sure we append our final message to ret
    ret.append(out)
    return ret


def print_food(person, search):
    """Prints a list of a user's inventory into discord message-sized chunks."""
    name = person.nick if person.nick else person.plain_name

    inventory = person.get_food()
    

    lock_template = "**%s (:lock:)**: %s. *(value: %s, %s ea)*\n"
    unlock_template = "**%s**: %s. *(value: %s, %s ea)*\n"

    messages = [(lock_template if item.is_locked else unlock_template)
                % (
                    string.capwords(item.item.name),
                    '{:,}'.format(item.amount),
                    '{:,}'.format(item.total_value),
                    '{:,}'.format(item.item.value)
                ) for item in inventory]

    ret = []
    header = f"{config.ITEMS_EMOJI} __**{name.upper()}'S INVENTORY**__ {config.ITEMS_EMOJI}\n"
    out = header
    for message in messages:
        if len(out) + len(message) > 1800:
            ret.append(out)
            out = header
        out = out + message

    # Make sure we append our final message to ret
    ret.append(out)
    return ret

def print_pets(person):
    """Prints a formatted list of pets a user has."""

    user_pets = [item.item for item in person.get_pets()]
    all_pets = Item.all_pets()

    pets_header = f':cat: __**PETS**__ :dog:\n'
    messages = []
    out = pets_header
    for pet in all_pets:
        if pet in user_pets:
            out += f"**{string.capwords(pet.name)}**\n"
        else:
            out += f'{string.capwords(pet.name)}\n'

        if len(out) > 1900:
            messages.append(out)
            out = pets_header

    out += f'{len(user_pets)}/{len(all_pets)}'
    messages.append(out)
    return messages


def claim(person: User, name, number, other_person=None):
    """Claims items/xp from an item and returns a message."""
    item = Item.objects.filter(name__iexact=name)[0]
    if not item:
        return f"{name} is not an item."

    if not person.has_item_amount_by_name(name, number):
        return f'You do not have {item.pluralize(number)} in your inventory.'

    out = ':moneybag: __**CLAIM**__ :moneybag:\n'
    if item == GEM_ROCK:
        out += 'You have received:\n'
        gems = {
            SAPPHIRE: 4,
            EMERALD: 16,
            RUBY: 64,
            DIAMOND: 128,
            LAPIS_LAZULI: 256,
            QUARTZ: 512
        }
        loot = Counter()
        for _ in range(number):
            while True:
                gem_type = random.sample(gems.keys(), 1)[0]
                if random.randint(1, gems[gem_type]) == 1:
                    loot[gem_type] += 1
                    break
        person.update_inventory(loot)
        for gem in loot.keys():
            out += f'{gem.pluralize(loot[gem])}\n'
        out += f'from your {GEM_ROCK.pluralize(number)}.'
        person.update_inventory({GEM_ROCK: number}, remove=True)
    elif item == ANCIENT_EFFIGY:
        skills = Counter()
        for _ in range(number):
            skill = random.sample(person.xp_fields_str, 1)[0]
            skills[skill] += 1
        person.update_inventory({OPENED_ANCIENT_EFFIGY: number})
        person.update_inventory({ANCIENT_EFFIGY: number}, remove=True)
        got_pet = False
        if not person.has_item_amount_by_item(EFFY, 1):
            for _ in range(number):
                if random.randint(1, 100) == 1:
                    got_pet = True
                    person.update_inventory({EFFY: 1})
                    break

        out += f"You have received the following xp from your {ANCIENT_EFFIGY.pluralize(number)}!\n"
        for skill in skills.keys():
            xp_gained = skills[skill] * XP_PER_EFFIGY
            setattr(person, skill, getattr(person, skill) + xp_gained)
            xp_gained_formatted = '{:,}'.format(xp_gained)
            out += f"{xp_gained_formatted} {skill.replace('_', ' ')}\n"
        if got_pet:
            out += 'You have also recieved Effy, the Effigy Pet!'
        person.save()
    elif item == CHRISTMAS_CRACKER:
        if other_person:
            person.update_inventory({CHRISTMAS_CRACKER: number}, remove=True)
            loot = Counter(random.choices(Item.objects.filter(name__contains="partyhat"), k=number))
            other_person_name = other_person.nick if other_person.nick else other_person.plain_name
            out += f'You and {other_person_name} pull the christmas cracker and '
            if random.randint(0, 1):
                out += f'**you** get the bigger end. You have received:\n'
                person.update_inventory(loot)
            else:
                out += f'**{other_person_name}** gets the bigger end. They have received:\n'
                other_person.update_inventory(loot)
            for item, value in loot.items():
                out += f'**{item.pluralize(value)}**\n'
        else:
            out += f'Please use the `~pull [number] [other_person]` command to claim the christmas crackers.'
    else:
        out += f'{item} is not claimable.'
    return out


def eat(author, item):
    if item == 'none' or item == 'nothing':
        author.active_food = None
        author.save()
        return f'You are now eating nothing.'

    try:
        item = Item.find_food_by_name(item)[0]
    except IndexError:
        # No food matching what was sent in
        return f'You cannot eat {item.name}.'
    if item in Item.all_food():
        author.active_food = item
        author.save()
        # TODO: Readd the pluaralization here per this comment
        # return f'You are now eating {items.add_plural(0, itemid)}!'
        return f'You are now eating {item.name}'
    else:
        return f'You cannot eat {item.name}.'


def equip_item(author: User, item: str):
    """Takes an item out of a user's inventory and places it into their equipment."""
    found_item = Item.find_by_name_or_nick(item)
    if found_item is None:
        return f'Error: {item} does not exist.'

    item_level = found_item.level
    user_cb_level = author.combat_level

    # Error checking/verification
    if user_cb_level < item_level:
        return f'Error: Insufficient level to equip item ({found_item.level}). \
                Your current combat level is {user_cb_level}.'

    if not author.has_item_by_item(found_item):
        return f'Error: {found_item.name} not in inventory.'

    if not found_item.is_equippable:
        return f'Error: {item} cannot be equipped.'

    if found_item.is_max_only and not author.is_maxed:
        return f"You cannot equip this item since you do not have {author.max_possible_level} skill total."

    slot = found_item.slot - 1  # I blame coiz for starting this at slot 1 :ANGERY:
    curr_equip = author.equipment_slots[slot]

    # if found_item == curr_equip:
    #     return f"You already have {found_item.name} equipped!"

    item_name = found_item.name
    slot_name = author.equipment_slot_strs[slot]

    # Set the equipment slot
    setattr(author, slot_name, found_item)

    # Update the inventories
    author.update_inventory(curr_equip)
    author.update_inventory(found_item, remove=True)

    author.save()
    return f'{item_name} equipped to {SLOTS[str(slot+1)]}!'


def unequip_item(author: User, item: str):
    """Takes an item out of a user's equipment and places it into their inventory."""
    found_item = Item.find_by_name_or_nick(item)
    if not found_item:
        return f'Error: {item} does not exist.'

    item_name = found_item.name
    equipment = author.all_armour

    if found_item not in author.equipment_slots:
        return f'You do not have {item_name} equipped.'

    slot = found_item.slot - 1
    slot_name = author.equipment_slot_strs[slot]
    curr_equip = author.equipment_slots[slot]

    # Set the equipment slot
    setattr(author, slot_name, None)
    author.update_inventory(curr_equip)
    author.save()
    return f'{found_item.name} unequipped from {SLOTS[str(slot+1)]}!'


def bury(author: User, itemname: str, number: int):
    """Buries (a given amount) of an item and gives the user prayer xp."""

    item: Item = Item.find_by_name_or_nick(itemname)
    if not item:
        return f'Error: {itemname} is not an item.'

    if not item.is_buryable:
        return f"You cannot bury {item.name}."

    user_items = author.get_item_by_item(item)
    if not author.has_item_amount_by_item(item, number) or not user_items:
        # TODO: Pluralize this
        return f'You do not have enough {item.name} in your inventory.'

    user_item: UserInventory = user_items[0]
    xp_difference = item.xp * number
    pre_bury_level = author.prayer_level

    author.prayer_xp += xp_difference
    author.save()

    if user_item.amount == number:
        user_item.delete()
    else:
        user_item.amount -= number
        user_item.save()

    post_bury_level = author.prayer_level
    level_difference = post_bury_level - pre_bury_level
    prayer_xp_formatted = '{:,}'.format(xp_difference)

    out = PRAYER_HEADER
    out += f'You get {prayer_xp_formatted} prayer xp from your {item.pluralize(number)}! '
    if level_difference:
        out += f'You have also gained {level_difference} prayer levels!'
    return out


def print_item_stats(itemname: str):
    """Prints the stats of an item."""
    item: Item = Item.find_by_name_or_nick(itemname)
    if not item:
        return f'Error: {itemname} is not an item.'

    name = string.capwords(item.name)
    value = '{:,}'.format(item.value)
    aliases = ', '.join(item.alias_strings)


    out = f'__**:moneybag: ITEMS :moneybag:**__\n'
    out += f'**Name**: {name}\n'
    if len(aliases) > 0:
        out += f'**Aliases**: {aliases}\n'
    out += f'**Value**: {value} gp\n'

    if item.slot > 0:
        damage = item.damage if item.damage else 0
        accuracy = item.accuracy if item.accuracy else 0
        prayer = item.prayer if item.prayer else 0
        level = item.level if item.level else 1
        armour = item.armour if item.armour else 0

        out += f'\n**Damage**: {damage}\n'
        out += f'**Accuracy**: {accuracy}\n'
        out += f'**Armour**: {armour}\n'
        out += f'**Prayer Bonus**: {prayer}\n'
        out += f'**Slot**: {string.capwords(SLOTS[str(item.slot)])}\n'
        out += f'**Combat Requirement**: {level}\n'
    if item.is_gatherable:
        xp = item.xp
        level = item.level if item.level else 1
        out += f'**Gather Requirement**: {level}\n'
        out += f'**xp**: {xp}\n'

    out += "\n**Drop Sources:**"
    dropping_monsters = item.monsterloot_set.all().order_by('rarity')
    ml: MonsterLoot
    for ml in dropping_monsters:
        if ml.min_amount == ml.max_amount:
            amt = ml.min_amount
        else:
            amt = "%d-%d" % (ml.min_amount, ml.max_amount)

        out += f'\n{string.capwords(ml.monster.name)} _(amount: {amt}, rarity: {ml.rarity_str})_'

    out += clue_helpers.print_item_from_lootable(item)
    return out

def format_as_table(content):
    # First line should be table headers
    # Each line after that should be the same length as content[0] and match
    # Every entry in content is a list of strings. If you send a non-string it will probably fail
    
    headers = content[0]
    # Figure out the length of each column based on the longest item in the column
    lens = [0] * len(headers)
    for i in range(0, len(headers)):
        for line in content:
            if len(line[i]) > lens[i]:
                lens[i] = len(line[i])

    out = "|"
    for i, header in enumerate(headers):
        out += header.rjust(lens[i]) + " |"
    out += "\n|"

    for line in content[1:]:
        for i, field in enumerate(line):
            out += field.rjust(lens[i]) + " |"
        out += "\n|"

    print(out)
    return out



