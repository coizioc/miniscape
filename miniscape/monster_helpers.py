import random
from miniscape.models import Monster, User


def get_random(author: User, wants_boss=False):
    """Randomly selects and returns a monster (given a particular boolean key)."""

    monster: Monster
    if wants_boss:
        monster = random.sample(set(Monster.objects.filter(is_boss=True)), 1)
    else:
        if author.offhand_slot.is_anti_dragon:
            monster = random.sample(set(Monster.objects.filter(is_boss=False,
                                                               is_slayable=True,
                                                               slayer_level_req__lte=author.slayer_level)), 1)
        else:
            monster = random.sample(set(Monster.objects.filter(is_boss=False,
                                                               is_slayable=True,
                                                               slayer_level_req__lte=author.slayer_level,
                                                               is_dragon=False)), 1)
    return monster[0]
