from miniscape.models import Monster, User, MonsterLoot
import random

CHARACTER_HEADER = f':crossed_swords: __**$NAME**__ :crossed_swords:\n'

RARITY_NAMES = {
        1: 'always',
        16: 'common',
        128: 'uncommon',
        256: 'rare',
        1024: 'super rare',
        4096: 'ultra rare',
        8192: 'super duper rare'
    }

AFFINITIES = {
    0: "Melee",
    1: "Range",
    2: "Magic",
    3: "None"
}


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


def print_monster_kills(author, search=None):
    """Prints the number of monsters a user has killed."""
    monster_kills = author.monster_kills(search)
    out = f"{CHARACTER_HEADER.replace('$NAME', author.plain_name)}"

    for monster in monster_kills:
        out += f'**{monster.monster.name.title()}**: {monster.amount}\n'
        pass

    return out

def find_by_name(name):
    """Finds a monster's ID from its name."""
    name = name.lower()
    for monsterid in list(MONSTERS.keys()):
        if name == MONSTERS[monsterid][NAME_KEY]:
            return monsterid
        if name == add_plural(0, monsterid):
            return monsterid
        if any([name == nick for nick in get_attr(monsterid, key=NICK_KEY)]):
            return monsterid
    else:
        raise KeyError

def print_list():
    """Prints a string containing a list of all monsters."""
    header = '__**:skull_crossbones: BESTIARY :skull_crossbones:**__\n'
    messages = []
    monster_list = []
    for monster in Monster.objects.all():
        level = monster.level
        name = monster.name
        slayer_req = monster.slayer_level_req
        monster_list.append((level, name, slayer_req))
    out = header
    for level, name, req in sorted(monster_list):
        out += f'**{name.title()}** *(combat: {level}'
        if int(req) > 1:
            out += f', slayer: {req}'
        out += ')*\n'
        if len(out) >= 1800:
            messages.append(out)
            out = header
    messages.append(out)
    return messages


def print_monster(monstername):
    """Prints information related to a monster."""
    monster: Monster
    monster = Monster.find_by_name_or_nick(monstername.lower())
    if not monster:
        return [f'Error: {monster} is not a monster.']

    messages = []
    aliases = ', '.join(monster.alias_strings)

    out = f'__**:skull_crossbones: BESTIARY :skull_crossbones:**__\n'\
          f'**Name**: {monster.name.title()}\n'

    if aliases:
        out += f'**Aliases**: {aliases}\n'
    if monster.quest_req:
        out += f'**Quest Requirement**: {monster.quest_req.name.title()}\n'
    if monster.slayer_level_req > 1:
        out += f'**Slayer Requirement**: {monster.slayer_level_req}\n'

    out += f'**Level**: {monster.level}\n'
    out += f'**Accuracy**: {monster.accuracy}\n'
    out += f'**Damage**: {monster.damage}\n'
    out += f'**Armour**: {monster.armour}\n'
    out += f'**Affinity**: {monster.affinity}\n'
    out += f'**XP**: {monster.xp}\n\n'
    out += f'**Loot Table**:\n'

    loot_table = monster.loot_table

    ml: MonsterLoot
    for ml in loot_table:
        out += f"{ml.item.name} *(amount: "
        if ml.min_amount == ml.max_amount:
            out += f'{ml.min_amount}, '
        else:
            out += f"{ml.min_amount}-{ml.max_amount}, "

        out += f"rarity: {ml.rarity_str})*\n"

        if len(out) >= 1800:
            messages.append(out)
            out = f'__**:skull_crossbones: BESTIARY :skull_crossbones:**__\n'

    messages.append(out)
    return messages
