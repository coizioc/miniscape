import math
import random
import ujson
from collections import Counter

from cogs.helper import items
from cogs.helper import prayer
from cogs.helper import users
from config import RECIPE_JSON, XP_FACTOR



with open(RECIPE_JSON, 'r') as f:
    RECIPES = ujson.load(f)

ARTISAN_REQ_KEY = 'artisan'
COOKING_REQ_KEY = 'cook'
QUEST_REQ_KEY = 'quest req'
INPUTS_KEY = 'inputs'
DEFAULT_RECIPE = {
    ARTISAN_REQ_KEY: 1,
    COOKING_REQ_KEY: 1,
    QUEST_REQ_KEY: [],
    INPUTS_KEY: Counter()
}













def get_attr(recipeid, key=INPUTS_KEY):
    """Gets an recipe's attribute from its id."""
    recipeid = str(recipeid)
    if recipeid in set(RECIPES.keys()):
        try:
            return RECIPES[recipeid][key]
        except KeyError:
            RECIPES[recipeid][key] = DEFAULT_RECIPE[key]
            return RECIPES[recipeid][key]
    else:
        raise KeyError















