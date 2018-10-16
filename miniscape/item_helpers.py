from miniscape.models import Item
from collections import Counter


def get_loot_value(loot: Counter):
    amt = 0
    for item, amount in loot.items():
        amt += amount * item.value
    return amt

def compare(item1, item2):
    """Prints a string comparing the stats of two given items."""
    i1: Item = Item.find_by_name_or_nick(item1)
    i2: Item = Item.find_by_name_or_nick(item2)

    if not i1:
        return f'Error: {item1} does not exist.'
    if not i2:
        return f'Error: {item2} does not exist.'

    out = f':moneybag: __**COMPARE**__ :moneybag:\n'\
          f'**{i1.name.title()} vs {i2.name.title()}:**\n\n'\
          f'**Accuracy**: {i1.accuracy} vs {i2.accuracy} *({i1.accuracy - i2.accuracy})*\n' \
          f'**Damage**: {i1.damage} vs {i2.damage} *({i1.damage - i2.damage})*\n' \
          f'**Armour**: {i1.armour} vs {i2.armour} *({i1.armour - i2.armour})*\n' \
          f'**Prayer Bonus**: {i1.prayer} vs {i2.prayer} *({i1.prayer - i2.prayer})*'
    return out