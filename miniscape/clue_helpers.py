import math
import string
import random
from collections import Counter

from cogs.helper import items
from cogs.helper import monsters as mon
from config import CLUES_DIRECTORY
from miniscape.item_helpers import get_loot_value
from miniscape.models import User, Quest, Item, ClueLoot
from miniscape import adventures as adv

DIFFICULTY = {
    1: 'easy',
    2: 'medium',
    3: 'hard',
    4: 'elite',
    5: 'master'
}

CLUE_HEADER = f':map: __**CLUE SCROLL**__ :map:\n'

EASY_CLUE_SCROLL_ID = 184
ROLLS_PER_CLUE = 5


def calc_length(userid, difficulty):
    """Calculates the time it takes to do a clue scroll."""
    user = User.objects.get(id=userid)
    quests_completed = user.num_quests_complete
    num_of_quests = len(Quest.objects.all())
    player_damage = user.damage + 1

    quest_multiplier = min((6 - difficulty) * quests_completed / num_of_quests, 1)

    base_time = 450 * difficulty

    time = base_time / (quest_multiplier * player_damage / 200)

    if time/base_time < 0.8:
        time = 0.8 * base_time
    return round(time)


def get_clue_scroll(person, *args):

    try:
        difficulty, length = args[0]
    except ValueError as e:
        print(e)
        raise ValueError

    user = User.objects.get(id=person)

    difficulty = int(difficulty)
    itemname = DIFFICULTY[difficulty] + ' clue scroll'
    item = Item.objects.get(name=itemname)

    loot = get_loot(item)
    user.update_inventory(loot)

    attr_name = DIFFICULTY[difficulty] + '_clues'
    setattr(user, attr_name, getattr(user, attr_name, 0) + 1)
    user.save()

    out = f'{CLUE_HEADER}' \
          f'<@{person}>, you have finished your {DIFFICULTY[int(difficulty)]} clue scroll! ' \
          f'You have received the following items:\n'
    out += print_loot(loot, item)

    return out


def get_loot(item: Item, factor=1):
    """Generates a Counter of loot from a given clue scroll difficulty."""

    loot_table = set(get_loot_table(item))
    loot = Counter()
    for _ in range(ROLLS_PER_CLUE):
        for _ in range(round(5 * factor)):
            item = random.sample(loot_table, 1)[0]
            if random.randint(1, item.rarity) == 1 and int(item.rarity) > 1:
                loot[item.loot_item] += random.randint(item.min_amount,
                                                       item.max_amount)
    return loot


def get_loot_table(item: Item):
    """Creates and returns a dictionary of possible loot from a clue scroll."""
    return ClueLoot.objects.filter(clue_item=item)


def get_rares(item: Item):
    return ClueLoot.objects.filter(clue_item=item).filter(rarity__gte=256)


def print_clue_scrolls(author):
    """Prints the number of clues a user has completed."""
    out = f'{CLUE_HEADER}'
    for clue in author.clue_counts:
        out += f'**{string.capwords(clue[0])}**: {clue[1]}\n'

    return out


def print_clue_scrolls(author):
    """Prints the number of clues a user has completed."""
    out = f'{CLUE_HEADER}'
    for clue in author.clue_counts:
        out += f'**{string.capwords(clue[0])}**: {clue[1]}\n'

    return out


def print_item_from_lootable(item):
    out = '\n'

    for cl in ClueLoot.objects.filter(loot_item=item):
        out += f'{string.capwords(cl.clue_item.name)} *(amount: '
        if cl.min_amount == cl.max_amount:
            out += f'{cl.min_amount}, '
        else:
            out += f'{cl.min_amount}-{cl.max_amount}, '
        out += f'rarity: {cl.rarity_str})*\n'

    return out


def print_loot(loot: Counter, item: Item):
    """Converts a user's loot from a clue scroll to a string."""
    out = ''
    rares = set(get_rares(item))
    for loot_item, amount in loot.items():
        if loot_item in rares:
            out += f'**{loot_item.pluralize(amount)}**\n'
        else:
            out += f'{loot_item.pluralize(amount)}\n'

    total_value = '{:,}'.format(get_loot_value(loot))
    out += f'*Total value: {total_value}*'

    return out


def print_status(userid, time_left, *args):
    """Prints a clue scroll and how long until it is finished."""
    difficulty, length = args[0]
    out = f'{CLUE_HEADER}' \
          f'You are currently doing a {DIFFICULTY[int(difficulty)]} clue scroll for {length} minutes. ' \
          f'You will finish {time_left}. '
    return out


def start_clue(guildid, channelid, userid, difficulty):
    """Starts a clue scroll."""
    user = User.objects.get(id=userid)
    out = f'{CLUE_HEADER}'
    if not adv.is_on_adventure(userid):
        scrollid = str(EASY_CLUE_SCROLL_ID + difficulty - 1)
        scroll = Item.objects.get(id=scrollid)
        if not user.has_item_by_item(scroll):
            return f'Error: you do not have a {scroll.name} in your inventory.'
        user.update_inventory(Counter({scroll: 1}), remove=True)

        length = math.floor(calc_length(userid, difficulty) / 60)
        clue = adv.format_line(4, userid, adv.get_finish_time(length * 60), guildid, channelid, difficulty, length)
        adv.write(clue)
        out += f'You are now doing a {DIFFICULTY[difficulty]} clue scroll for {length} minutes.'
    else:
        out = adv.print_adventure(userid)
        out += adv.print_on_adventure_error('clue scroll')
    user.save()
    return out
