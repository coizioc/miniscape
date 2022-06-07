"""This module contains methods that handle items and their attributes."""

from config import ITEMS_EMOJI


NAME_KEY = 'name'           # Name of the item
PLURAL_KEY = 'plural'       # string containing how to pluralise an item's name.
NICK_KEY = 'nick'           # list of nicknames for an item.
VALUE_KEY = 'value'         # High alch value of the item
DAMAGE_KEY = 'damage'       # Damage stat of the item
ACCURACY_KEY = 'accuracy'   # Accuracy stat of the item
ARMOUR_KEY = 'armour'       # Armour stat of the item
PRAYER_KEY = 'prayer'       # Prayer drain bonus of the item.
SLOT_KEY = 'slot'           # Slot item can be equipped
AFFINITY_KEY = 'aff'        # Item affinity, 0:Melee, 1:Range, 2:Magic
LEVEL_KEY = 'level'         # Level item can be equipped/gathered
XP_KEY = 'xp'               # xp gained for gathering/crafting the item.
QUEST_KEY = 'quest req'     # quest required to gather an item.
TALISMAN_KEY = 'talisman'   # Itemid of the talisman needed in inventory to craft rune.
POUCH_KEY = 'pouch'         # Int representing how many extra rune essence can be held per trip.
GATHER_KEY = 'gather'       # Boolean whether item can be gathered.
TREE_KEY = 'tree'           # Boolean whether gatherable is a tree.
ROCK_KEY = 'rock'           # Boolean whether gatherable is a rock.
FISH_KEY = 'fish'           # Boolean whether gatherable is a fish.
POT_KEY = 'potion'          # Boolean whether consumable is a potion.
RUNE_KEY = 'rune'           # Boolean whether item is a rune.
COOK_KEY = 'cook'           # Boolean whether item can be cooked.
BURY_KEY = 'bury'           # Boolean whether item can be buried.
MAX_KEY = 'max'		        # Boolean whether max skill total is a req to wear item.
PET_KEY = 'pet'             # Boolean whether item is a pet.
EAT_KEY = 'eat'             # Int representing chance improvement by item when set as food.
LUCK_KEY = 'luck'           # float representing factor of luck enhancement
DEFAULT_ITEM = {NAME_KEY: 'unknown item',
                PLURAL_KEY: 's',
                NICK_KEY: [],
                VALUE_KEY: 0,
                DAMAGE_KEY: 0,
                ACCURACY_KEY: 0,
                ARMOUR_KEY: 0,
                PRAYER_KEY: 0,
                SLOT_KEY: 0,
                AFFINITY_KEY: 0,
                LEVEL_KEY: 1,
                XP_KEY: 1,
                QUEST_KEY: 0,
                TALISMAN_KEY: -1,
                POUCH_KEY: 0,
                GATHER_KEY: False,
                TREE_KEY: False,
                ROCK_KEY: False,
                FISH_KEY: False,
                POT_KEY: False,
                COOK_KEY: False,
                BURY_KEY: False,
                RUNE_KEY: False,
                MAX_KEY: False,
                PET_KEY: False,
                EAT_KEY: 0,
                LUCK_KEY: 1
                }

SHOP_HEADER = f'{ITEMS_EMOJI} __**SHOP**__ {ITEMS_EMOJI}\n'



