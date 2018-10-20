import config
CHARACTER_HEADER = f'{config.COMBAT_EMOJI} __**$NAME**__ {config.COMBAT_EMOJI}\n'


def print_equipment(author, name=None, with_header=False):
    """Writes a string showing the stats of a user's equipment."""

    if with_header and name is not None:
        out = f"{CHARACTER_HEADER.replace('$NAME', name.upper())}"
    else:
        out = ''

    damage, accuracy, armour, prayer = author.equipment_stats
    out += f'**Damage**: {damage}\n' \
           f'**Accuracy**: {accuracy}\n' \
           f'**Armour**: {armour}\n' \
           f'**Prayer Bonus**: {prayer}\n'

    if author.prayer_slot:
        out += f'**Active Prayer**: {author.prayer_slot.name}\n'
    else:
        out += f'**Active Prayer**: none\n'

    if author.active_food:
        out += f'**Active Food**: {author.active_food.name}\n\n'
    else:
        out += f'**Active Food**: none\n\n'

    equipment = author.all_armour
    for slot in author.all_armour_print_order:
        item = equipment[slot]
        out += f'**{slot.title()}**: '
        if item is not None:
            out += item.formatted_item_stats
        else:
            out += 'none *(dam: 0, acc: 0, arm: 0, pray: 0)*\n'

    return out
