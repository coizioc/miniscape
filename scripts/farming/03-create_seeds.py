from miniscape.models import Item, ItemNickname
from miniscape.models.farming_plot import TREE_PATCH, BUSH_PATCH, ALLOTMENT_PATCH, FRUIT_TREE_PATCH, FLOWER_PATCH, \
    HERB_PATCH


class seed:
    def __init__(self, name, level, patch_type, nicknames, plural, value, xp):
        self.name = name
        self.level = level
        self.patch_type = patch_type
        self.nicknames = nicknames
        self.plural = plural
        self.value = value
        self.xp = xp

    def create_and_persist_object(self):
        try:
            i = Item.objects.get(name=self.name)
        except Item.DoesNotExist:
            i = Item(
                name=self.name,
                plural=self.plural,
                value=self.value,
                is_farmable=True,
            )
            i.save()

        for nick in self.nicknames:
            try:
                ItemNickname.objects.get(nickname=nick)
            except ItemNickname.DoesNotExist:
                nn = ItemNickname(real_item=i, nickname=nick)
                nn.save()


TREE_SEEDS = {
    "acorn": seed("acorn", 15, TREE_PATCH.identifier, [], "s", 1000, 500),
    "willow": seed("willow tree seed", 30, TREE_PATCH.identifier, ["willow seed"], "s", 3000, 1500),
    "maple": seed("maple tree seed", 45, TREE_PATCH.identifier, ["maple seed"], "s", 7500, 3500),
    "yew": seed("yew tree seed", 60, TREE_PATCH.identifier, ["yew seed"], "s", 20000, 7000),
    "magic": seed("magic tree seed", 75, TREE_PATCH.identifier, ["magic seed"], "s", 50000, 14000),
    "elder": seed("elder tree seed", 90, TREE_PATCH.identifier, ["elder seed"], "s", 100000, 25000)
}

BUSH_SEEDS = {
    "redberry": seed("redberry seed", 8, BUSH_PATCH.identifier, [], "s", 100, 50),
    "dwellberry": seed("dwellberry seed", 20, BUSH_PATCH.identifier, [], "s", 200, 200),
    "whiteberry": seed("whiteberry seed", 60, BUSH_PATCH.identifier, [], "s", 5000, 450),
    "poison ivy": seed("poison ivy seed", 70, BUSH_PATCH.identifier, [], "s", 10000, 800),
    "avocado": seed("avocado seed", 80, BUSH_PATCH.identifier, [], "s", 15000, 4000),
    "cactuss": seed("cactuss seed", 95, BUSH_PATCH.identifier, ["guncle seed", "cactussy"], "s", 25000, 15000)
}

ALLOTMENT_SEEDS = {
    "potato": seed("potato seed", 1, ALLOTMENT_PATCH.identifier, [], "s", 3, 9),
    "onion": seed("onion seed", 5, ALLOTMENT_PATCH.identifier, [], "s", 7, 11),
    "cabbage": seed("cabbage seed", 10, ALLOTMENT_PATCH.identifier, [], "s", 11, 15),
    "strawberry": seed("strawberry seed", 20, ALLOTMENT_PATCH.identifier, [], "s", 30, 29),
    "snape grass": seed("snape grass seed", 50, ALLOTMENT_PATCH.identifier, [], "s", 70, 80),
}

FRUIT_TREE_SEEDS = {
    "apple": seed("apple tree seed", 15, FRUIT_TREE_PATCH.identifier, [], "s", 1000, 900),
    "banana": seed("banana tree seed", 27, FRUIT_TREE_PATCH.identifier, [], "s", 1776, 2200),
    "orange": seed("orange tree seed", 39, FRUIT_TREE_PATCH.identifier, [], "s", 2048, 3000),
    "papaya": seed("papaya tree seed", 58, FRUIT_TREE_PATCH.identifier, [], "s", 6200, 7000),
    "palm": seed("palm tree seed", 69, FRUIT_TREE_PATCH.identifier, [], "s", 9999, 12000),
    "mango": seed("mango tree seed", 95, FRUIT_TREE_PATCH.identifier, [], "s", 250000, 30000)
}

FLOWER_SEEDS = {
    "marigold": seed("marigold seed", 1, FLOWER_PATCH.identifier, [], "s", 3, 25),
    "peony": seed("peony seed", 5, FLOWER_PATCH.identifier, [], "s", 10, 50),
    "limpwurt": seed("limpwurt root seed", 15, FLOWER_PATCH.identifier, ["limp seed"], "s", 20, 90),
    "hydrangea": seed("hydrangea seed", 50, FLOWER_PATCH.identifier, ["hydr seed"], "s", 50, 400)
}

HERB_SEEDS = {
    "guam seed": seed("guam seed", 1, HERB_PATCH.identifier, [], "s", 3, 13),
    "irit seed": seed("irit seed", 40, HERB_PATCH.identifier, [], "s", 120, 45),
    "toadflax seed": seed("toadflax seed", 35, HERB_PATCH.identifier, [], "s", 110, 40)
}


def create_tree_seeds():
    for s in TREE_SEEDS.values():
        s.create_and_persist_object()


def create_bush_seeds():
    for s in BUSH_SEEDS.values():
        s.create_and_persist_object()


def create_allotment_seeds():
    for s in ALLOTMENT_SEEDS.values():
        s.create_and_persist_object()


def create_fruit_tree_seeds():
    for s in FRUIT_TREE_SEEDS.values():
        s.create_and_persist_object()


def create_flower_seeds():
    for s in FLOWER_SEEDS.values():
        s.create_and_persist_object()


def create_herb_seeds():
    for s in HERB_SEEDS.values():
        s.create_and_persist_object()
