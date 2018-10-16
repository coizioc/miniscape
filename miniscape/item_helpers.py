from miniscape.models import Item
from collections import Counter


def get_loot_value(loot: Counter):
    amt = 0
    for item, amount in loot.items():
        amt += amount * item.value
    return amt
