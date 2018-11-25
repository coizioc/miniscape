import random
from collections import Counter

from config import VIS_SHOP_FILE, NUM_VIS_PREFERENCES, SEED_OFFSET, VIS_BASE_COST, VIS_DELTA
from miniscape.models.periodicchecker import PeriodicChecker
from miniscape.models.item import Item, VisRunes
from miniscape.itemconsts import VIS_WAX

VIS_SHOP = {}
with open(VIS_SHOP_FILE, 'r') as f:
    for line in f.read().splitlines():
        line_split = line.split(';')
        VIS_SHOP[line_split[0]] = {}
        VIS_SHOP[line_split[0]]['number'] = int(line_split[1])
        VIS_SHOP[line_split[0]]['cost'] = int(line_split[2])

SHOP_HEADER = '__**:moneybag: SHOP :moneybag:**__\n'


def calc_cost(attempts):
    """Calculates the number of runes required for each slot with a given attempt."""
    # A given attempt will increase the change in the number of runes needed by VIS_DELTA. That is to say:
    # dy/dx = VIS_DELTA * x. Thus integrating, we get y = (VIS_DELTA / 2) * x^2 + BASE_COST.
    return round((VIS_DELTA / 2) * ((attempts - 1) ** 2) + VIS_BASE_COST)


def calc_num(userid, user_runes):
    """Calculates how much vis wax a user will recieve with the given runes."""
    vis_runes = get_vis_runes(userid)

    num_vis = [0, 0, 0]
    for i, user_rune in enumerate(user_runes):
        for j, vis_rune in enumerate(vis_runes[i]):
            if user_rune.id == vis_rune.rune.id:
                num_vis[i] += 40 / 2 ** j if i == 0 else 30 - j / 2 ** j
                break
    return num_vis


def get_vis_runes(userid):
    """Generates the runes for vis wax."""
    seed_int = int(PeriodicChecker.objects.get(id=1).last_check_datetime.timestamp() + SEED_OFFSET)
    random.seed(seed_int)
    vis_runes = list(VisRunes.objects.all())

    runes = random.choices(vis_runes, k=NUM_VIS_PREFERENCES * 4)

    rune1 = runes[:NUM_VIS_PREFERENCES]

    rune2 = []
    slot2_offset = userid % 3
    for i in range(NUM_VIS_PREFERENCES):
        rune2.append(runes[NUM_VIS_PREFERENCES + i + 2 * slot2_offset])

    rune3 = []
    for i in range(NUM_VIS_PREFERENCES):
        rune3.append(runes[(userid + (i + 1) * seed_int) % len(vis_runes)])

    return rune1, rune2, rune3


def parse_rune_names(names):
    """Gets the runes from"""
    rune1 = Item.find_by_name_or_nick(names[0] + " rune")
    if not rune1:
        raise ValueError("First rune not found.")
    rune2 = Item.find_by_name_or_nick(names[1] + " rune")
    if not rune2:
        raise ValueError("Second rune not found.")
    rune3 = Item.find_by_name_or_nick(names[2] + " rune")
    if not rune2:
        raise ValueError("Third rune not found.")
    return rune1, rune2, rune3


def print_vis_result(user, names, use=False):
    if len(names) != 3:
        return "You must enter exactly three runes to input into the Vis Wax Machine."
    try:
        user_runes = parse_rune_names(names)
    except ValueError as e:
        return str(e)

    num_vis = calc_num(user.id, user_runes)
    if not use:
        user.vis_attempts += 1
    cost = calc_cost(user.vis_attempts)
    if use:
        for user_rune, number in Counter(user_runes).items():
            if not user.has_item_amount_by_item(user_rune, cost * number):
                cost_formatted = '{:,}'.format(cost * number)
                return 'You do not have enough %s to use this combination of runes (%s)'\
                       % (user_rune.name, cost_formatted)

    use_format = 'You have used the runes %s, %s, and %s, receiving %d, %d, and %d vis wax respectively, ' \
                 'for a total of %d vis wax! This will cost %s runes for each slot. You have made %d attempts today.'
    not_use_format = 'With the runes %s, %s, and %s, you would receive %d, %d, and %d vis wax respectively, for a ' \
                     'total of %d vis wax. This would cost %s runes for each slot. You have made %d attempts today.'
    cost_formatted = '{:,}'.format(cost)
    out = (use_format if use else not_use_format) % (user_runes[0].name, user_runes[1].name, user_runes[2].name, num_vis[0],
                                                     num_vis[1], num_vis[2], sum(num_vis), cost_formatted,
                                                     user.vis_attempts)

    if use:
        user.update_inventory({VIS_WAX: sum(num_vis)})
        for user_rune, number in Counter(user_runes).items():
            user.update_inventory({user_rune: number * cost}, remove=True)
        user.is_vis_complete = 1
    user.save()
    return out


def shop_buy(user, name, number=1):
    """Buys an item from the vis wax shop."""
    item = Item.find_by_name_or_nick(name)
    if not item:
        return f'{name} is not an item.'

    itemid = str(item.id)
    try:
        vis_cost = VIS_SHOP[itemid]['cost']
    except KeyError:
        return f'{item.name} not in vis shop.'

    if not user.has_item_amount_by_item(VIS_WAX, number * vis_cost):
        return f'You do not have enough vis wax to purchase this many {item.name}'
    vis_num = VIS_SHOP[itemid]['number']
    user.update_inventory({VIS_WAX: number * vis_cost}, remove=True)
    user.update_inventory({item: number * vis_num})
    return f'You have purchased {vis_num} {item.name} for {number * vis_cost} vis wax!'


def shop_print():
    """Prints the vis wax shop."""
    out = f'{SHOP_HEADER}'
    for itemid in VIS_SHOP.keys():
        name = Item.objects.get(id=itemid).name
        out += f"{VIS_SHOP[itemid]['number']} {name}: {VIS_SHOP[itemid]['cost']} vis wax\n"
    return out
