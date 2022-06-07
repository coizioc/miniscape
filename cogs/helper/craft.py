from collections import Counter

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



