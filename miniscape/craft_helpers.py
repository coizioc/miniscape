import math
from collections import Counter
import random

from config import XP_FACTOR
from miniscape import prayer_helpers
from miniscape.models import Item, User, Recipe, Prayer, RecipeRequirement, Quest

GATHER_HEADER = f':hammer_pick: __**GATHERING**__ :hammer_pick: \n'
CRAFT_HEADER = f':hammer_pick: __**CRAFTING**__ :hammer_pick: \n'

RUNE_ESSENCE = Item.objects.get(name__iexact="rune essence")
PURE_ESSENCE = Item.objects.get(name__iexact="pure essence")
COOK_GAUNTLETS = Item.objects.get(name__iexact="cooking gauntlets")
GOLD_GAUNTLETS = Item.objects.get(name__iexact="goldsmithing gauntlets")
GOLD_BAR_RECIPE = Recipe.objects.get(creates__name__iexact="gold bar")
CRYSTAL_ROD = Item.objects.get(name__iexact="Crystal Fishing Rod")
LIGHT_FORM = Prayer.objects.get(name__iexact="light form")
BURNT_FOOD = Item.objects.get(name__iexact="burnt food")
RUNE_MYSTERIES = Quest.objects.get(name__iexact="rune mysteries")
ABYSS_QUEST = Quest.objects.get(name__iexact="Enter the Abyss")
POUCHES = list(Item.objects.filter(pouch__gt=0))


def start_gather(guildid, channelid, user: User, itemname, length=-1, number=-1):
    """Starts a gathering session."""
    from miniscape import adventures as adv

    out = ''
    userid = user.id
    if not adv.is_on_adventure(userid):

        item: Item = Item.find_by_name_or_nick(itemname)
        if not item:
            return f'Error: {item} is not an item.'

        try:
            length = int(length)
            number = int(number)
        except ValueError:
            return f'Error: {length} is not a valid length of time.'

        if not item.is_gatherable:
            return f'Error: you cannot gather item {ite.name}.'

        quest_req = item.quest_req
        if quest_req and quest_req not in user.completed_quests_list:
            return f'Error: You do not have the required quest to gather this item.'

        item_name = item.name
        gather_level = user.gather_level
        gather_requirement = item.level
        player_potion = user.potion_slot.id if user.potion_slot else '0'

        if player_potion == 435:
            boosted_level = gather_level + 3
        elif player_potion == 436:
            boosted_level = gather_level + 6
        else:
            boosted_level = gather_level

        if boosted_level < gather_requirement:
            return f'Error: {item_name} has a gathering requirement ({gather_requirement}) higher ' \
                   f'than your gathering level ({gather_level})'

        # Adjust the number approppriately
        if number > 1000 and gather_level == 99:
            number = 1000
        if number > 500 and gather_level < 99:
            number = 500
        if length > 180:
            length = 180

        if int(number) < 0:
            number = calc_number(user,item, length * 60)
            if number > 500:
                number = 500
        elif int(length) < 0:
            length = math.floor(calc_length(user, item, number)[1] / 60)
        else:
            return 'Error: argument missing (number or kill length).'
        gather = adv.format_line(3, userid, adv.get_finish_time(length * 60), guildid, channelid,
                                 item.id, item_name, number, length)
        adv.write(gather)
        out += f'You are now gathering {item.pluralize(number)} for {length} minutes.'
    else:
        out = adv.print_adventure(userid)
        out += adv.print_on_adventure_error('gathering')
    return out


def print_status(userid, time_left, *args):
    """Prints a gathering and how long until it is finished."""
    itemid, item_name, number, length = args[0]
    item = Item.objects.get(id=itemid)
    out = f'{GATHER_HEADER}' \
          f'You are currently gathering {item.pluralize(number)} for {length} minutes. ' \
          f'You will finish {time_left}. '
    return out


def print_rc_status(userid, time_left, *args):
    """Prints a gathering and how long until it is finished."""
    itemid, item_name, number, length, pure = args[0]
    item = Item.objects.get(id=itemid)
    out = f'{GATHER_HEADER}' \
          f'You are currently crafting {item.pluralize(number)} for {length} minutes. ' \
          f'You will finish {time_left}. '
    return out


def print_recipe(user, recipe):
    """Prints details related to a particular recipe."""

    created_item = Item.find_by_name_or_nick(recipe)
    recipe = Recipe.objects.filter(creates=created_item)
    if not recipe:
        return f'Error: cannot find recipe that crafts {recipe}.'
    recipe = recipe[0]

    out = f'{CRAFT_HEADER}'\
          f'**Name**: {created_item.name.title()}\n'\
          f'**Artisan Requirement**: {recipe.level_requirement}\n'\
          f'**XP Per Item**: {created_item.xp}\n'\
          f'**Inputs**:\n'

    item_requirements = RecipeRequirement.objects.filter(recipe=recipe)
    for requirement in item_requirements:
        if user.has_item_by_item(requirement.item):
            out += f'~~{requirement.item.pluralize(requirement.amount)}~~\n'
        else:
            out += f'{requirement.item.pluralize(requirement.amount)}\n'

    return out


def print_list(user: User, search):
    """Prints a list of the recipes a user can use."""
    # completed_quests = set(users.get_completed_quests(userid))
    messages = []
    out = f'{CRAFT_HEADER}'
    recipes = Recipe.objects.all().order_by('level_requirement', 'creates__name')
    if search:
        recipes = recipes.filter(creates__name__icontains=search)

    recipes = list(recipes)
    user_quests = user.completed_quests_list
    for recipe in recipes:
        if recipe.quest_requirement in user_quests:
            out += f'**{recipe.creates.name.title()}** *(level {recipe.level_requirement})*\n'

        if len(out) > 1800:
            messages.append(out)
            out = f'{CRAFT_HEADER}'

    out += 'Type `~recipes info [item]` to get more info about how to craft a particular item.'
    messages.append(out)
    return messages


def get_runecraft(person, *args):
    """Gets the result of a runecrafting session."""
    try:
        itemid, item_name, number, length, pure = args[0]
        number = int(number)
        pure = int(pure)
    except ValueError as e:
        print(e)
        raise ValueError
    user = User.objects.get(id=person.id)
    item = Item.objects.get(id=itemid)

    if not user.has_item_amount_by_item(RUNE_ESSENCE, number) \
        and not user.has_item_amount_by_item(PURE_ESSENCE, number):
        return f"{person.mention}, your session did not net you any xp " \
               f"because you did not have enough rune essence."

    rc_level_before = user.rc_level
    rc_req = item.level
    loot = Counter({item: int(number * (1 + (rc_level_before - rc_req) / 20))})
    xp = XP_FACTOR * number * item.xp

    if pure:
        xp *= 2

    user.update_inventory(loot)

    if pure:
        loot = Counter({PURE_ESSENCE: number})
    else:
        loot = Counter({RUNE_ESSENCE: number})
    user.update_inventory(loot, remove=True)
    user.rc_xp += xp
    rc_level_after = user.rc_level

    xp_formatted = '{:,}'.format(xp)
    out = f'{GATHER_HEADER}' \
          f'{person.mention}, your runecrafting session has finished! You have crafted ' \
          f'{item.pluralize(number)} and have gained {xp_formatted} runecrafting xp! '
    if rc_level_after > rc_level_before:
        out += f'In addition, you have gained {rc_level_after - rc_level_before} runecrafting levels!'
    user.potion_slot = None
    user.save()
    return out


def get_gather_list():
    """Gets list of all gatherable items."""
    gatherables = Item.objects.filter(is_gatherable=True).order_by('level', 'name')
    messages = []
    out = GATHER_HEADER
    for item in gatherables:
        out += f'**{item.name.title()}** *(level: {item.level}, ' \
               f'xp: {item.xp})*\n'
        if len(out) > 1800:
            messages.append(out)
            out = GATHER_HEADER

    messages.append(out)
    return messages


def get_gather(person, *args):
    try:
        itemid, item_name, number, length = args[0]
        number = int(number)
    except ValueError as e:
        print(e)
        raise ValueError
    user = User.objects.get(id=person.id)
    item = Item.objects.get(id=itemid)
    user.update_inventory({item: number})
    xp = XP_FACTOR * number * item.xp
    gather_level_before = user.gather_level
    user.gather_xp += xp
    gather_level_after = user.gather_level

    xp_formatted = '{:,}'.format(xp)
    out = f'{GATHER_HEADER}' \
          f'{person.mention}, your gathering session has finished! You have gathered ' \
          f'{item.pluralize(number)} and have gained {xp_formatted} gathering xp! '

    if gather_level_after > gather_level_before:
        out += f'In addition, you have gained {gather_level_after - gather_level_before} gathering levels!'
    user.potion_slot = None
    user.save()
    return out


def calc_burn(user: User, item: Item):
    """Calculates the burn chance for a given food."""
    cook_level = user.cook_level
    cook_req = item.level
    c = 10 if COOK_GAUNTLETS in user.equipment_slots else 0

    chance = max(100 * ((cook_level - cook_req + c) / 20), 20)
    return 100 - min(100, chance)


def calc_length(user: User, item: Item, number):
    """Calculates the length of gathering a number of an item."""
    user_prayer = user.prayer_slot
    gather_level = user.gather_level
    item_xp = item.xp
    item_level = item.level

    if item.is_tree:
        if user.equipment_slots[12]:
            item_multiplier = 2 - user.equipment_slots[12].level/100
        else:
            item_multiplier = 10
    elif item.is_rock:
        if user.equipment_slots[13]:
            item_multiplier = 2 - user.equipment_slots[13].level / 100
        else:
            item_multiplier = 10
    elif item.is_fish:
        if CRYSTAL_ROD in user.equipment_slots:
            item_multiplier = 1.3
        else:
            item_multiplier = 2
    else:
        item_multiplier = 2

    time_multiplier = gather_level / item_level
    base_time = math.floor(number * item_xp * (100 - item_level) / 200)
    time = item_multiplier * base_time / time_multiplier

    if user_prayer == LIGHT_FORM:
        prayer_time = prayer_helpers.calc_drain_time(user)
        if prayer_time < time:
            time /= max(1, 1.5 * prayer_time / time)
        else:
            time /= 1.5

    return base_time, round(time)


def calc_number(user: User, item: Item, time):
    """Calculates the number of items that can be gathered in a given time period."""
    gather_level = user.gather_level
    item_xp = item.xp
    item_level = item.level
    if item.is_tree:
        if user.equipment_slots[12]:
            item_multiplier = 2 - user.equipment_slots[12].level/100
        else:
            item_multiplier = 10
    elif item.is_rock:
        if user.equipment_slots[13]:
            item_multiplier = 2 - user.equipment_slots[13].level / 100
        else:
            item_multiplier = 10
    elif item.is_fish:
        if CRYSTAL_ROD in user.equipment_slots:
            item_multiplier = 1.3
        else:
            item_multiplier = 2
    else:
        item_multiplier = 2

    time_multiplier = gather_level / item_level
    number = math.floor(time * time_multiplier / (item_xp * item_multiplier * ((100 - item_level) / 200)))
    return number


def craft(user: User, recipe, n=1):
    """Crafts (a given number of) an item."""

    recipeitem: Item = Item.find_by_name_or_nick(recipe)
    if not recipeitem:
        return f'Cannot find item {recipe}.'

    recipe: Recipe = Recipe.objects.filter(creates=recipeitem)
    if not recipe:
        return f'Cannot find recipe that crafts {recipeitem.name}.'
    recipe = recipe[0]

    name = recipeitem.name
    artisan_level = user.artisan_level
    artisan_req = recipe.level_requirement
    if artisan_level < artisan_req:
        return f'Error: {name} has a artisan requirement ({artisan_req}) ' \
               f'higher than your artisan level ({artisan_level}).'

    inputs = recipe.get_requirements()
    for rr in list(inputs):
        if user.has_item_amount_by_item(rr.item, rr.amount*n):
            negative_loot = {rr.item: rr.amount}
        else:
            return f'Error: you do not have enough items to make {recipe.creates.pluralize(n)} ' \
                   f'({rr.item.pluralize(rr.amount * n)}).'

    bonus = random.randint(1, math.floor(n/20)) if artisan_level == 99 and n >=20 else 0

    goldsmith_bonus = 1
    if recipe == GOLD_BAR_RECIPE and GOLD_GAUNTLETS in user.equipment_slots:
        goldsmith_bonus = 2

    user.update_inventory(negative_loot, remove=True)
    user.update_inventory({recipe.creates: n + bonus})
    xp = XP_FACTOR * goldsmith_bonus * n * recipe.creates.xp
    user.artisan_xp += xp
    level_after = user.artisan_level

    xp_formatted = '{:,}'.format(xp)
    out = f'Successfully crafted {recipe.creates.pluralize(n)}! You have also gained {xp_formatted} artisan xp! '
    if bonus > 0:
        out += f'Due to your 99 artisan perk, you have also created an extra {recipe.creates.pluralize(bonus)}! '
    if level_after > artisan_level:
        out += f'You have also gained {level_after - artisan_level} artisan levels!'
    return out


def cook(user: User, food, n=1):
    """Cooks (a given number of) an item."""

    item: Item = Item.find_by_name_or_nick(food)
    if not item:
        return f'Cannot find food called {food} that can be cooked.'

    name = item.name
    cooking_level = user.cook_level
    cooking_req = item.level
    if cooking_level < cooking_req:
        return f'{name} has a cooking requirement ({cooking_req}) higher than your cooking level ({cooking_level}).'


    rr = RecipeRequirement.objects.filter(recipe__creates=item)
    if user.has_item_amount_by_item(rr.item, rr.amount*n):
        negative_loot = {rr.item: rr.amount}
    else:
        return f'Error: you do not have enough items to make {recipe.item.pluralize(n)} ' \
               f'({rr.item.pluralize(rr.amount * n)}).'

    burn_chance = calc_burn(user, item)
    num_cooked = 0
    bonus = 0
    if burn_chance == 0:
        num_cooked = n
    else:
        for _ in range(n):
            if random.randint(1, 100) > burn_chance:
                num_cooked += 1
    if cooking_level == 99:
        for _ in range(n):
            if random.randint(1, 20) == 1:
                bonus += 1

    user.update_inventory(negative_loot, remove=True)
    user.update_inventory({item: num_cooked})
    user.update_inventory({BURNT_FOOD: n - num_cooked})
    xp = XP_FACTOR * num_cooked * item.xp
    user.cook_xp += xp
    level_after = user.cook_level

    xp_formatted = '{:,}'.format(xp)
    out = f'After cooking {item.pluralize(n)}, you successfully cook ' \
          f'{num_cooked} and burn {n - num_cooked}! '
    if bonus > 0:
        out += f'Due to your cooking perk, you have also cooked an additional {item.pluralize(n)}! '
    out += f'You have also gained {xp_formatted} cooking xp! '
    if level_after > cooking_level:
        out += f'You have also gained {level_after - cooking_level} cooking levels!'
    return out


def start_runecraft(guildid, channelid, user: User, item, number=1, pure=0):
    """Starts a runecrafting session."""
    from miniscape import adventures as adv

    out = ''
    if not adv.is_on_adventure(user.id):
        item: Item = Item.find_by_name_or_nick(item)
        if not item:
            return f'{item} is not an item.'

        try:
            number = int(number)
        except ValueError:
            return f'{number} is not a valid number.'

        if not item.is_rune:
            return f'{items.get_attr(itemid)} is not a rune that can be crafted.'

        # Find out if user has the talisman
        rune_type = item.name.split(" ")[0]
        if not user.has_item_by_name(rune_type + " talisman"):
            return f'{items.get_attr(talismanid)} not found in inventory.'

        item_name = item.name
        runecrafting_level = user.rc_level
        runecraft_req = item.level
        player_potion = user.potion_slot.id if user.potion_slot else '0'

        if player_potion == 435:
            boosted_level = runecrafting_level + 3
        elif player_potion == 436:
            boosted_level = runecrafting_level + 6
        else:
            boosted_level = runecrafting_level

        if boosted_level < runecraft_req:
            return f'Error: {item_name} has a runecrafting requirement ({runecraft_req}) higher ' \
                   f'than your runecrafting level ({runecrafting_level})'

        if item.quest_req and not user.has_completed_quest(item.quest_req):
            return f'You do not have the required quest to craft this rune.'
        if not user.has_completed_quest(RUNE_MYSTERIES):
            return f'You do not know how to craft runes.'

        factor = 1 if user.has_completed_quest(ABYSS_QUEST) else 2
        bonus = 0
        for pouch in POUCHES:
            if user.has_item_by_item(pouch):
                bonus += pouch.pouch

        length = factor * math.ceil(number * 1.2 / (28.0 + bonus))
        ess_to_check = PURE_ESSENCE if pure else RUNE_ESSENCE
        if not user.has_item_amount_by_item(ess_to_check, number):
            return f'You do not have enough essence to craft this many runes.'

        rc_session = adv.format_line(6, user.id, adv.get_finish_time(length * 60), guildid, channelid,
                                     item.id, item_name, number, length, pure)
        adv.write(rc_session)
        out += f'You are now crafting {item.pluralize(number)} for {length} minutes.'
    else:
        out = adv.print_adventure(user.id)
        out += adv.print_on_adventure_error('runecrafting session')
    return out