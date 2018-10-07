import random
import time

from config import RUNEID_FILE, VIS_FILE, VIS_SHOP_FILE
from cogs.helper import items, users

# The way ~vis works is that there are three slots for runes to fit. Each are randomly selected each day.
#
# The first slot is the same for everyone. The second slot can be one of three runes, which are the same for everyone.
# The third slot is a random rune unique to each person. Each slot has a second preference based on the same criteria.
# As the number of attempts increase, the number of runes needed to make the vis wax increases.
#
# The vis file is stored as list of length 9. Here is what each element in the list represents:
# * 0: first choice of first slot; same for everyone.
# * 1: second choice of first slot; same for everyone.
# * 2: first of three first choices of second slot; same for everyone.
# * 3: first of three second choices of second slot; same for everyone.
# * 4: second of three first choices of second slot; same for everyone.
# * 5: second of three second choices of second slot; same for everyone.
# * 6: third of three first choices of second slot; same for everyone.
# * 7: third of three second choices of second slot; same for everyone.
# * 8: the unix timestamp for the current date.

RUNEIDS = {}
with open(RUNEID_FILE, 'r') as f:
    for line in f.read().splitlines():
        line_split = line.split(';')
        RUNEIDS[line_split[0]] = line_split[1]

VIS_SHOP = {}
with open(VIS_SHOP_FILE, 'r') as f:
    for line in f.read().splitlines():
        line_split = line.split(';')
        VIS_SHOP[line_split[0]] = {}
        VIS_SHOP[line_split[0]]['number'] = int(line_split[1])
        VIS_SHOP[line_split[0]]['cost'] = int(line_split[2])

BASE_COST = 2500
VIS_DELTA = 150


def calc(userid, runes_input):
    """Calculates the number of vis wax given the userid and a list of items.
    Returns a list of length 3 representing how many vis wax they have received in each slot."""
    runes = []
    for item in runes_input:
        try:
            itemid = items.find_by_name(item)
        except KeyError:
            return f"Cannot find item {item}."
        try:
            runes.append(RUNEIDS[itemid])
        except KeyError:
            return f"{items.get_attr(itemid)} is not a rune."

    vis = open_vis()
    num_vis = [0, 0, 0]
    if runes[0] == vis[0]:
        num_vis[0] += 40
    elif runes[0] == vis[1]:
        num_vis[0] += 20
    else:
        num_vis[0] += 10

    if runes[1] == vis[2 + 2 * (userid % 2)]:
        num_vis[1] += 30
    elif runes[1] == vis[3 + 2 * (userid % 2)]:
        num_vis[1] += 15
    else:
        num_vis[1] += 7

    if runes[2] == calc_third_rune(userid, vis[8]):
        num_vis[2] += 30
    elif runes[2] == calc_third_rune(userid, vis[8], best=False):
        num_vis[2] += 15
    else:
        num_vis[2] += 7

    return num_vis


def calc_num(attempts):
    """Calculates the number of runes required to produce vis wax given a number of attempts."""
    # A given attempt will increase the change in the number of runes needed by VIS_DELTA. That is to say:
    # dy/dx = VIS_DELTA * x. Thus integrating, we get y = (VIS_DELTA / 2) * x^2 + BASE_COST.
    return (VIS_DELTA / 2) * ((attempts - 1) ** 2) + BASE_COST


def calc_third_rune(userid, timestamp=None, best=True):
    if timestamp is None:
        timestamp = open_vis()[8]
    return RUNEIDS[(userid / timestamp) % len(RUNEIDS.keys())] if best else\
           RUNEIDS[(userid % timestamp) % len(RUNEIDS.keys())]


def open_vis():
    """Opens the vis wax list."""
    with open(VIS_FILE, 'r') as f:
        vis = f.read().splitlines()
    return vis


def shop_print():
    """Prints the vis wax shop."""
    out = f'{items.SHOP_HEADER}'
    for itemid in VIS_SHOP.keys():
        if VIS_SHOP[itemid]['number'] > 1:
            out += f"{items.add_plural(VIS_SHOP[itemid]['number'], itemid)}: "
        else:
            out += f'{items.get_attr(itemid)}: '
        out += f"{VIS_SHOP[itemid]['cost']} vis wax\n"
    return out


def shop_buy(userid, item, number=1):
    """Buys an item from the vis wax shop."""
    try:
        itemid = items.find_by_name(item)
    except KeyError:
        return f"{item} not found."

    item_name = items.get_attr(itemid)
    try:
        vis_cost = VIS_SHOP[itemid]['cost']
    except KeyError:
        return f'{item_name} not in vis shop.'

    if not users.item_in_inventory(userid, '579', number * vis_cost):
        return f'You do not have enough vis wax to purchase this many {item_name}'

    users.update_inventory(userid, number * vis_cost * ['579'], remove=True)
    users.update_inventory(userid, number * [itemid])
    return f'You have purchased {items.add_plural(number, itemid)} for {number * vis_cost} vis wax!'


def update_vis():
    """Changes the daily runes for vis wax."""
    vis = []
    for _ in range(8):
        vis.append(random.sample(RUNEIDS, k=1)[0])
    vis.append(int(time.time()))
    with open(VIS_FILE, 'w') as f:
        f.write('\n'.join(vis))
