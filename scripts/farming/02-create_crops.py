from miniscape.models import Item

class crop:
    def __init__(self, name, nicknames, plural, value, food_value):
        self.name = name
        self.nicknames = nicknames
        self.plural = plural
        self.value = value
        self.food_value = food_value


BUSH_CROPS = {
    "redberry": crop("redberries", [], "", 20, 0),
    "dwellberry": crop("dwellberries", [], "", 30, 0),
    "poison ivy": crop("poison ivy berries", ["poison ivy"], "", 100, 0),
    "avocado": crop("avocado", ["shavacado"], "es", 800, 15),
    "cactuss fruit": crop("cactuss fruit", ["cactuss"], "s", 1500, 18),
    "whiteberries": None,
}

ALLOTMENT_CROPS = {
    "potato": crop("potato", ["tater"], "es", 10, 2),
    "onion": crop("onion", ["shrek"], "s", 20, 3),
    "cabbage": crop("cabbage", [], "s", 30, 4),
    "strawberry": crop("strawberry", ["sberry"], "", 50, 5),
    "snape grass": None,
}

FRUIT_TREE_CROPS = {
    "apple": crop("apple", [], "s", 40, 5),
    "banana": crop("banana", ["nanner"], "s", 80, 7),
    "orange": crop("orange", [], "s", 120, 8),
    "papaya": crop("papaya", [], "s", 200, 12),
    "coconut": crop("coconut", [], "s", 500, 14),
    "mango": crop("mango", [], "es", 3000, 21)
}

FLOWER_CROPS = {
    "marigold": crop("marigold", [], "s", 20, 0),
    "peony": crop("peony", [], "s", 80, 0),
    "hydrangea": crop("hydrangea", [], "s", 20000, 0),
    "limpwurt root": None
}

"""
Toadflax Herb
Irit Herb
"""
HERB_CROPS = {

}

def create_bush_crops():
    pass
