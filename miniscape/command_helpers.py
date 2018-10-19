import config
from miniscape import clue_helpers
from miniscape.models import Item, User, UserInventory, MonsterLoot
import config
from config import ARMOUR_SLOTS_FILE


PRAYER_HEADER = f':pray: __**PRAYER**__ :pray:\n'


SLOTS = {}
with open(ARMOUR_SLOTS_FILE, 'r') as f:
    for line in f.read().splitlines()[1:]:
        line_split = line.split(';')
        SLOTS[line_split[0]] = line_split[1]


def print_inventory(person, search):
    """Prints a list of a user's inventory into discord message-sized chunks."""
    name = person.nick if person.nick else person.plain_name

    inventory = person.get_inventory(search)

    lock_template = "**%s (:lock:)**: %s. *(value: %s, %s ea)*\n"
    unlock_template = "**%s**: %s. *(value: %s, %s ea)*\n"

    messages = [(lock_template if item.is_locked else unlock_template)
                % (
                    item.item.name.title(),
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
            out +=  f"**{pet.name.title()}**\n"
        else:
            out += f'{pet.name.title()}\n'

        if len(out) > 1900:
            messages.append(out)
            out = pets_header

    out += f'{len(user_pets)}/{len(all_pets)}'
    messages.append(out)
    return messages


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
        return f'Error: {item_name} cannot be equipped.'

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

    author.pray_xp += xp_difference
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
        return f'Error: {item} is not an item.'

    name = item.name.title()
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
        out += f'**Slot**: {SLOTS[str(item.slot)].title()}\n'
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

        out += f'\n{ml.monster.name.title()} _(amount: {amt}, rarity: {ml.rarity_str})_'

    out += clue_helpers.print_item_from_lootable(item)
    return out



