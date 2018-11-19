from config import SHOP_FILE
from miniscape.models import Item, User, Quest
from collections import Counter

SHOP_HEADER = '__**:moneybag: SHOP :moneybag:**__\n'


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


def print_shop(userid):
    """Prints the shop."""
    user = User.objects.get(id=userid)
    items = open_shop()

    out = SHOP_HEADER
    messages = []
    for itemid, quest_id in items.items():
        item: Item = Item.objects.get(id=int(itemid))

        # Check if we have the quests for it
        is_available = False
        if not int(items[itemid]):
            is_available = True
        else:
            quest_req: Quest = Quest.objects.get(id=quest_id)
            if quest_req in user.completed_quests_list:
                is_available = True

        if is_available:
            name = item.name
            price = '{:,}'.format(4 * item.value)
            out += f'**{name.title()}**: {price} coins\n'

        if len(out) > 1800:
            messages.append(out)
            out = SHOP_HEADER
    messages.append(out)
    return messages


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
    user = User.objects.get(id=userid)
    item: Item = Item.find_by_name_or_nick(item)
    if not item:
        return f'Error: {item} is not an item.'

    try:
        number = int(number)
    except ValueError:
        return f'Error: {number} is not a number.'

    item_name = item.name
    if user.has_item_amount_by_item(item, number):
        value = item.value
        coin = Item.objects.get(name="coins")
        user.update_inventory(Counter({coin: value*number}))
        user.update_inventory(Counter({item: number}), remove=True)

        value_formatted = '{:,}'.format(value * number)
        return f'{number} {item_name} sold for {value_formatted} coins!'
    else:
        return f'Error: {item_name} not in inventory or you do not have at least {number} in your inventory.'


def buy(userid, item, number):
    """Buys (a given amount) of an item and places it in the user's inventory."""
    user = User.objects.get(id=userid)
    item: Item = Item.find_by_name_or_nick(item)
    if not item:
        return f'Error: {item} is not an item.'

    try:
        number = int(number)
    except ValueError:
        return f'Error: {number} is not a number.'

    item_name = item.name

    if item_in_shop(item.id):
        items = open_shop()
        quest_id = int(items[str(item.id)])
        quest_req = None
        if quest_id:
            quest_req = Quest.objects.get(id=quest_id)

        if not quest_id or user.has_completed_quest(quest_req):
            value = item.value
            cost = 4 * number * value
            coin = Item.objects.get(name="coins")
            if user.has_item_amount_by_item(coin, cost):
                user.update_inventory(Counter({coin: cost}), remove=True)
                user.update_inventory(Counter({item: number}))
                value_formatted = '{:,}'.format(4 * value * number)
                return f'{number} {item_name} bought for {value_formatted} coins!'
            else:
                return f'You do not have enough coins to buy this item. ({cost} coins)'
        else:
            return 'Error: You do not have the requirements to buy this item.'
    else:
        return f'Error: {item_name} not available in shop.'
