import random
import string

from django.db.models import Q

from miniscape.models import Monster, User, MonsterLoot

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

SLAYER_LEVEL_THRESHOLD = 0.8
SLAYER_CHANCE_THRESHOLD = 50


def get_random(author: User, wants_boss=False):
    """Randomly selects and returns a monster (given a particular boolean key)."""
    min_level = 0 if wants_boss else author.combat_level * SLAYER_LEVEL_THRESHOLD
    monsters = Monster.objects.filter(Q(quest_req=None) | Q(quest_req__in=author.completed_quests_list),
                                      Q(is_dragon__in=[False, author.offhand_slot.is_anti_dragon]),
                                      is_boss=wants_boss,
                                      is_slayable=not wants_boss,
                                      slayer_level_req__lte=author.slayer_level,
                                      level__gte=min_level)
    return random.sample(set(monsters), 1)[0]


def print_monster_kills(author, search=None):
    """Prints the number of monsters a user has killed."""
    monster_kills = author.monster_kills(search)
    out = f"{CHARACTER_HEADER.replace('$NAME', author.plain_name)}"

    for monster in monster_kills:
        out += f'**{string.capwords(monster.monster.name)}**: {monster.amount}\n'
        pass

    return out


def print_monster(monstername):
    """Prints information related to a monster."""
    monster: Monster
    monster = Monster.find_by_name_or_nick(monstername.lower())
    if not monster:
        return [f'Error: {monstername} is not a monster.']

    messages = []
    aliases = ', '.join(monster.alias_strings)

    out = f'__**:skull_crossbones: BESTIARY :skull_crossbones:**__\n' \
          f'**Name**: {string.capwords(monster.name)}\n'

    if aliases:
        out += f'**Aliases**: {aliases}\n'
    if monster.quest_req:
        out += f'**Quest Requirement**: {string.capwords(monster.quest_req.name)}\n'
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

        if ml.rarity > 1:
            out += f"rarity: {ml.rarity_str} (1/{ml.rarity}))*\n"
        else:
            out += f"rarity: {ml.rarity_str})*\n"

        if len(out) >= 1800:
            messages.append(out)
            out = f'__**:skull_crossbones: BESTIARY :skull_crossbones:**__\n'

    messages.append(out)
    return messages


def print_list(search="", allow_empty=True):
    """Prints a string containing a list of all monsters."""
    header = '__**:skull_crossbones: BESTIARY :skull_crossbones:**__\n'
    messages = []
    monster_list = []
    for monster in Monster.objects.filter(name__icontains=search):
        level = monster.level
        name = monster.name
        slayer_req = monster.slayer_level_req
        monster_list.append((level, name, slayer_req))

    if not monster_list and not allow_empty:
        return []

    out = header
    for level, name, req in sorted(monster_list):
        out += f'**{string.capwords(name)}** *(combat: {level}'
        if int(req) > 1:
            out += f', slayer: {req}'
        out += ')*\n'
        if len(out) >= 1800:
            messages.append(out)
            out = header

    out += 'Type `~bes [name]` to get more information about a particular monster.\n'
    messages.append(out)
    return messages
