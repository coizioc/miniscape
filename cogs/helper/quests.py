from collections import Counter

import ujson

from config import QUESTS_JSON, QUEST_EMOJI

with open(QUESTS_JSON, 'r') as f:
    QUESTS = ujson.load(f)

NAME_KEY = 'name'
DESCRIPTION_KEY = 'description'
SUCCESS_KEY = 'success'
FAILURE_KEY = 'failure'
ITEM_REQ_KEY = 'item req'
QUEST_REQ_KEY = 'quest req'
REWARD_KEY = 'reward'
DAMAGE_KEY = 'damage'
ACCURACY_KEY = 'accuracy'
ARMOUR_KEY = 'armour'
LEVEL_KEY = 'level'
DRAGON_KEY = 'dragon'
TIME_KEY = 'time'

DEFAULT_QUEST = {
    NAME_KEY: 'Untitled Quest',
    DESCRIPTION_KEY: 'Go something for this person and get some stuff in return.',
    SUCCESS_KEY: 'You did it!',
    FAILURE_KEY: "You didn't do it!",
    ITEM_REQ_KEY: Counter(),
    QUEST_REQ_KEY: [],
    REWARD_KEY: Counter(),
    DAMAGE_KEY: 1,
    ACCURACY_KEY: 1,
    ARMOUR_KEY: 1,
    LEVEL_KEY: 1,
    DRAGON_KEY: False,
    TIME_KEY: 10
}

QUEST_HEADER = f'{QUEST_EMOJI} __**QUESTS**__ {QUEST_EMOJI}\n'










