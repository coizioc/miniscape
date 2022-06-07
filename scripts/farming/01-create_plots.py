import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "miniscapebot.settings")
import django

django.setup()

from miniscape.models import Quest, FarmPlot
from miniscape.models.farming_plot import HERB_PATCH, ALLOTMENT_PATCH, BUSH_PATCH, TREE_PATCH, FRUIT_TREE_PATCH, \
    FLOWER_PATCH


def __get_quest(name):
    return Quest.objects.get(name__iexact=name)


def create_herb_patches():
    lumbridge = FarmPlot(name="Lumbridge herb patch",
                         nick="lumby",
                         type=HERB_PATCH.identifier,
                         quest_req=__get_quest("cook's assistant"))

    crandor = FarmPlot(name="Crandor herb patch",
                       nick="crandor",
                       type=HERB_PATCH.identifier,
                       quest_req=__get_quest("Dragon Slayer, Part 3"))

    east_ardougne = FarmPlot(name="East Ardougne herb patch",
                             nick="ardy",
                             type=HERB_PATCH.identifier,
                             quest_req=__get_quest("Dragon Slayer, Part 3"))

    haunted_mine = FarmPlot(name="Haunted Mine herb patch",
                         nick="mine",
                         type=HERB_PATCH.identifier,
                         quest_req=__get_quest("Haunted Mine"))
    lumbridge.save()
    crandor.save()
    east_ardougne.save()
    haunted_mine.save()
    return


def create_allotment_patches():
    al_kharid = FarmPlot(name="Al-Kharid allotment patch",
                         nick="al-kh",
                         type=ALLOTMENT_PATCH.identifier,
                         quest_req=__get_quest("Dragon Slayer, Part 3"))

    varrock = FarmPlot(name="Varrock allotment patch",
                       nick="varrock",
                       type=ALLOTMENT_PATCH.identifier,
                       quest_req=None)

    deaths_office = FarmPlot(name="Death's office allotment patch",
                             nick="deaths",
                             type=ALLOTMENT_PATCH.identifier,
                             quest_req=__get_quest("Missing, Presumed Death"))

    karamja = FarmPlot(name="Karamja allotment patch",
                             nick="karamja",
                             type=ALLOTMENT_PATCH.identifier,
                             quest_req=__get_quest("nature spirit"))
    al_kharid.save()
    varrock.save()
    deaths_office.save()
    karamja.save()
    return


def create_bush_patches():
    trollheim = FarmPlot(name="Trollheim bush patch",
                         nick="trollheim",
                         type=BUSH_PATCH.identifier,
                         quest_req=__get_quest("Eadgar's Ruse"))

    shilo = FarmPlot(name="Shilo Village office bush patch",
                     nick="Shilo",
                     type=BUSH_PATCH.identifier,
                     quest_req=__get_quest("Shilo Village"))

    lunar_isle = FarmPlot(name="Lunar Isle bush patch",
                          nick="lunar",
                          type=BUSH_PATCH.identifier,
                          quest_req=__get_quest("Lunar Diplomacy"))

    pyramid = FarmPlot(name="Desert Pyramid bush patch",
                       nick="pyramid",
                       type=BUSH_PATCH.identifier,
                       quest_req=__get_quest("Desert Treasure, Part 3"))
    trollheim.save()
    shilo.save()
    lunar_isle.save()
    pyramid.save()
    return


def create_tree_patches():
    falador = FarmPlot(name="Falador Tree patch",
                       nick="fally",
                       type=TREE_PATCH.identifier,
                       quest_req=None)

    tai_bwo_wannai = FarmPlot(name="Tai Bwo Wannai Tree patch",
                              nick="tai",
                              type=TREE_PATCH.identifier,
                              quest_req=__get_quest("nature spirit"))

    watchtower = FarmPlot(name="Watchtower Tree patch",
                          nick="watchtower",
                          type=TREE_PATCH.identifier,
                          quest_req=__get_quest("the watchtower"))

    ape_atoll = FarmPlot(name="Ape Atoll Tree patch",
                         nick="ape",
                         type=TREE_PATCH.identifier,
                         quest_req=__get_quest("monkey madness"))
    falador.save()
    tai_bwo_wannai.save()
    watchtower.save()
    ape_atoll.save()
    return


def create_fruit_tree_patches():
    tzhaar_city = FarmPlot(name="Tzhaar City Fruit Tree patch",
                           nick="tzhaar",
                           type=FRUIT_TREE_PATCH.identifier,
                           quest_req=__get_quest("The Brink of Extinction"))

    meiyerditch = FarmPlot(name="Meiyerditch Fruit Tree patch",
                           nick="meiyer",
                           type=FRUIT_TREE_PATCH.identifier,
                           quest_req=__get_quest("Darkness of Hallovale"))

    froze_prison = FarmPlot(name="Nex's Frozen Prison Fruit Tree patch",
                           nick="nex",
                           type=FRUIT_TREE_PATCH.identifier,
                           quest_req=__get_quest("The Frozen Prison"))

    etc = FarmPlot(name="Etceteria Fruit Tree patch",
                           nick="etc",
                           type=FRUIT_TREE_PATCH.identifier,
                           quest_req=__get_quest("Royal Trouble"))
    tzhaar_city.save()
    meiyerditch.save()
    froze_prison.save()
    etc.save()
    return


def create_flower_patches():
    zanaris = FarmPlot(name="Zanaris flower patch",
                       nick="zanaris",
                       type=FLOWER_PATCH.identifier,
                       quest_req=__get_quest("The Lost City"))

    camelot = FarmPlot(name="Camelot flower patch",
                       nick="camelot",
                       type=FLOWER_PATCH.identifier,
                       quest_req=__get_quest("merlin's crystal"))

    lighthouse = FarmPlot(name="Lighthouse flower patch",
                          nick="lighthouse",
                          type=FLOWER_PATCH.identifier,
                          quest_req=__get_quest("Horror from the Deep"))

    misc = FarmPlot(name="Miscellania Flower patch",
                           nick="misc",
                           type=FLOWER_PATCH.identifier,
                           quest_req=__get_quest("Royal Trouble"))
    zanaris.save()
    camelot.save()
    lighthouse.save()
    misc.save()
    pass


def main():
    create_flower_patches()
    create_fruit_tree_patches()
    create_tree_patches()
    create_allotment_patches()
    create_bush_patches()
    create_herb_patches()
    return


if __name__ == "__main__":
    main()
