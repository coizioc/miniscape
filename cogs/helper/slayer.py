import math
import random

from miniscape import adventures as adv
from cogs.helper import items
from cogs.helper import monsters as mon
from cogs.helper import prayer
from cogs.helper import users
from config import XP_FACTOR, SLAYER_EMOJI, COMBAT_EMOJI

LOWEST_NUM_TO_KILL = 35

SLAYER_HEADER = f'{SLAYER_EMOJI} __**SLAYER**__ {SLAYER_EMOJI}\n'
KILLING_HEADER = f'{COMBAT_EMOJI} __**COMBAT**__ {COMBAT_EMOJI}\n'





