import datetime
import json
import logging
import math
import string
from collections import Counter
import random
import discord

import utils.command_helpers
from miniscape import adventures as adv
from config import XP_FACTOR, MAX_PER_ACTION
from mbot import MiniscapeBotContext
from miniscape import prayer_helpers, command_helpers
from utils.command_helpers import parse_number_and_name
from miniscape.models import Item, User, Recipe, Prayer, RecipeRequirement, Quest, Task
from config import GATHER_EMOJI, ARTISAN_EMOJI, RC_EMOJI
from discord import Embed

GATHER_HEADER = f'{GATHER_EMOJI} __**GATHERING**__ {GATHER_EMOJI}\n'
CRAFT_HEADER = f'{ARTISAN_EMOJI} __**CRAFTING**__ {ARTISAN_EMOJI}\n'
RUNECRAFT_HEADER = f'{RC_EMOJI} __**RUNECRAFTING**__ {RC_EMOJI}\n'

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
RUNES = list(Item.objects.filter(is_rune=True).order_by("level"))


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
            return f'Error: you cannot gather item {item.name}.'

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
            number = calc_number(user, item, length * 60)
            if number > 500:
                number = 500
        elif int(length) < 0:
            length = math.floor(calc_length(user, item, number)[1] / 60)
        else:
            return 'Error: argument missing (number or kill length).'
        gather = utils.command_helpers.format_adventure_line(3, userid, utils.command_helpers.calculate_finish_time(length * 60), guildid, channelid,
                                                             item.id, item_name, number, length)
        adv.write(gather)
        out += f'You are now gathering {item.pluralize(number)} for {length} minutes.'
    else:
        out = adv.print_adventure(userid)
        out += utils.command_helpers.print_on_adventure_error('gathering')
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


def print_rc_status2(task: Task, time_left):
    out = ""
    extra_data = json.loads(task.extra_data)
    item = Item.objects.get(id=extra_data["item_id"])
    out += f"You are currently crafting {item.pluralize(extra_data['num'])} " \
           f"for {extra_data['length']} minutes.\n" \
           f"You will finish in {time_left} minutes\n"
    return out


def print_recipe(user, recipe_name):
    """Prints details related to a particular recipe."""

    created_item = Item.find_by_name_or_nick(recipe_name)
    recipe = Recipe.objects.filter(creates=created_item)
    if not recipe:
        return f'Error: cannot find recipe that crafts {recipe_name}.'
    recipe = recipe[0]

    out = f'{CRAFT_HEADER}' \
          f'**Name**: {string.capwords(created_item.name)}\n' \
          f'**Artisan Requirement**: {recipe.level_requirement}\n' \
          f'**XP Per Item**: {created_item.xp}\n' \
          f'**Inputs**:\n'

    item_requirements = RecipeRequirement.objects.filter(recipe=recipe)
    for requirement in item_requirements:
        if user.has_item_by_item(requirement.item):
            out += f'~~{requirement.item.pluralize(requirement.amount)}~~\n'
        else:
            out += f'{requirement.item.pluralize(requirement.amount)}\n'

    return out


def print_list(user: User, search, filter_quests=True, allow_empty=True):
    """Prints a list of the recipes a user can use.
    user: the user object to compare quest completion
    search: a string to search through recipe names
    filter_quests: whether to filter results based on completed quests or not"""
    messages = []
    out = f'{CRAFT_HEADER}'
    recipes = Recipe.objects.all().order_by('level_requirement', 'creates__name')
    if search:
        recipes = recipes.filter(creates__name__icontains=search)

    recipes = list(recipes)
    if not recipes and not allow_empty:
        return []
    user_quests = user.completed_quests_list
    for recipe in recipes:
        msg = f'**{string.capwords(recipe.creates.name)}** *(level {recipe.level_requirement})*\n'

        # if we're filtering on quests, only add the recipe if it either doesn't have a quest req
        # or the req is met
        if filter_quests:
            if not recipe.quest_requirement or \
                    recipe.quest_requirement in user_quests:
                out += msg
        else:
            # Otherwise add it unconditionally
            out += msg

        if len(out) > 1800:
            messages.append(out)
            out = f'{CRAFT_HEADER}'

    out += 'Type `~recipes info [item]` to get more info about how to craft a particular item.\n'
    messages.append(out)
    return messages


def get_runecraft2(task: Task):
    # Keys: "item_id", "num", "length", "is_pure"
    extra_data = json.loads(task.extra_data)
    item = Item.objects.get(id=extra_data["item_id"])
    number = extra_data["num"]
    is_pure = extra_data["is_pure"]
    user = task.user

    # Check that they didnt' sell/trade the essence since they started
    ess_to_check = PURE_ESSENCE if is_pure else RUNE_ESSENCE
    if not task.user.has_item_amount_by_item(ess_to_check, number):
        return f"Your session did not net you any xp because you " \
               f"didn't have enough {ess_to_check.name}"

    # Calculate the number of runes crafted and subsequent xp
    rc_level_before = user.rc_level
    rc_req = item.level
    loot = Counter({item: int(number * (1 + (rc_level_before - rc_req) / 20))})
    xp = XP_FACTOR * number * item.xp

    if is_pure:
        xp *= 2

    # Give the user the runes
    user.update_inventory(loot)

    # Remove the essence
    user.update_inventory(Counter({ess_to_check: number}))

    # Award xp
    user.rc_xp += xp

    rc_level_after = user.rc_level
    user.potion_slot = None
    user.save()

    xp_formatted = '{:,}'.format(xp)
    out = f'{RUNECRAFT_HEADER}' \
          f'Your runecrafting session has finished! You have crafted ' \
          f'{item.pluralize(number)} and have gained {xp_formatted} runecrafting xp! '
    if rc_level_after > rc_level_before:
        out += f'In addition, you have gained {rc_level_after - rc_level_before} runecrafting levels!'

    return out


def get_runecraft(person, *args):
    """Gets the result of a runecrafting session."""
    try:
        itemid, item_name, number, length, pure = args[0]
        number = int(number)
        pure = int(pure)
    except ValueError as e:
        print(e)
        raise ValueError
    user = User.objects.get(id=person)
    item = Item.objects.get(id=itemid)

    if not user.has_item_amount_by_item(RUNE_ESSENCE, number) \
            and not user.has_item_amount_by_item(PURE_ESSENCE, number):
        return f"<@{person}>, your session did not net you any xp " \
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
    user.potion_slot = None
    user.save()

    xp_formatted = '{:,}'.format(xp)
    out = f'{RUNECRAFT_HEADER}' \
          f'<@{person}>, your runecrafting session has finished! You have crafted ' \
          f'{item.pluralize(number)} and have gained {xp_formatted} runecrafting xp! '
    if rc_level_after > rc_level_before:
        out += f'In addition, you have gained {rc_level_after - rc_level_before} runecrafting levels!'

    return out


def get_gather_list():
    """Gets list of all gatherable items."""
    gatherables = Item.objects.filter(is_gatherable=True).order_by('level', 'name')
    messages = []
    out = GATHER_HEADER
    for item in gatherables:
        out += f'**{string.capwords(item.name)}** *(level: {item.level}, ' \
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
    user = User.objects.get(id=person)
    item = Item.objects.get(id=itemid)
    user.update_inventory({item: number})
    xp = XP_FACTOR * number * item.xp
    gather_level_before = user.gather_level
    user.gather_xp += xp
    gather_level_after = user.gather_level

    xp_formatted = '{:,}'.format(xp)
    out = f'{GATHER_HEADER}' \
          f'<@{person}>, your gathering session has finished! You have gathered ' \
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
            item_multiplier = 2 - user.equipment_slots[12].level / 100
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
            item_multiplier = 2 - user.equipment_slots[12].level / 100
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
    negative_loot = {}
    for rr in list(inputs):
        if user.has_item_amount_by_item(rr.item, rr.amount * n):
            negative_loot[rr.item] = rr.amount * n
        else:
            return f'Error: you do not have enough items to make {recipe.creates.pluralize(n)} ' \
                   f'({rr.item.pluralize(rr.amount * n)}).'

    bonus = random.randint(1, math.floor(n / 20)) if artisan_level == 99 and n >= 20 else 0

    goldsmith_bonus = 1
    if recipe == GOLD_BAR_RECIPE and GOLD_GAUNTLETS in user.equipment_slots:
        goldsmith_bonus = 2

    user.update_inventory(negative_loot, remove=True)
    user.update_inventory({recipe.creates: n + bonus})
    xp = XP_FACTOR * goldsmith_bonus * n * recipe.creates.xp
    user.artisan_xp += xp
    user.save()
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
    if not rr:
        return "You cannot cook {name}."
    rr = rr[0]
    if user.has_item_amount_by_item(rr.item, rr.amount * n):
        negative_loot = {rr.item: rr.amount * n}
    else:
        return f'You do not have enough items to make {rr.item.pluralize(n)} ' \
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
        bonus = random.randint(0, round(n / 20))

    user.update_inventory(negative_loot, remove=True)
    user.update_inventory({item: num_cooked})
    user.update_inventory({BURNT_FOOD: n - num_cooked})
    xp = XP_FACTOR * num_cooked * item.xp
    user.cook_xp += xp
    user.save()
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


def start_runecraft2(ctx: MiniscapeBotContext, *args, pure=False):
    out = discord.Embed(title="Runecrafting", type="rich", description=RUNECRAFT_HEADER)

    # Do all of our error checking first
    number, rune = parse_number_and_name(args)

    # Check we were able to parse the rune they want to craft and a number from it
    if not (number and rune):
        out.description += "Invalid input. Correct format is `~rc <number> <rune>`"
        return out

    # Is our user already busy?
    user: User = ctx.user_object
    if adv.is_on_adventure(user.id):
        out.description += "You are already on an adventure!\n\n"
        out.description += adv.print_adventure(user.id)
        out.description += utils.command_helpers.print_on_adventure_error('runecrafting session')
        return out

    # Have they completed rune mysteries?
    if not user.has_completed_quest(RUNE_MYSTERIES):
        out.description += "You do not know how to craft runes, yet"
        return out

    # Does the thing they requested exist, and is it a rune?
    requested_rune = Item.find_by_name_or_nick(rune)
    if not requested_rune:
        out.description += f"{rune} is not an item"
        return out

    if not requested_rune.is_rune:
        out.description += f"{requested_rune.name} is not a craftable rune."
        return out

    # Do they have the required talisman?
    talisman = requested_rune.name.rstrip("rune") + "talisman"
    if not user.has_item_by_name(talisman):
        out.description += f'{talisman} not present in inventory'
        return out

    # Do they have the required level?
    if user.rc_level < requested_rune.level:
        out.description += f"*ERROR*: {requested_rune.name} has a runecrafting requirement ({requested_rune.level}) " \
                           f"than your runecrafting level ({user.rc_level})"
        return out

    # Have they completed the quest requirement for this rune (if it exists)?
    # TODO: As of now, no runes have a quest req (they probably should)
    if requested_rune.quest_req and not user.has_completed_quest(requested_rune.quest_req):
        out.description += f"You do not have the required quest ({string.capwords(requested_rune.quest_req.name)}) " \
                           f"to craft this rune."
        return out

    # If they're trying to craft too many, hamstring 'em
    if number > MAX_PER_ACTION:
        out.description += f"_reducing number to {MAX_PER_ACTION} from {number}._\n"
        number = MAX_PER_ACTION

    # What kind of essence should we use? Do they have enough?
    ess_to_use = PURE_ESSENCE if pure else RUNE_ESSENCE
    if not user.has_item_amount_by_item(ess_to_use, number):
        out.description += f"You do not have enough {ess_to_use.name} to craft this many runes"
        return out

    # Figure out our speed boosts. Factor is basically "What speed can we run there?", with higher numbers
    # being better (higher speed). Capacity is how many essence can we take with us per trip. Pouches increase this
    factor = 1 if user.has_completed_quest(ABYSS_QUEST) else 2
    capacity = 28  # 28 is the base capacity
    for pouch in POUCHES:
        if user.has_item_by_item(pouch):
            capacity += pouch.pouch

    # Now, calculate how long this will take
    length = factor * math.ceil(number * 1.2 / capacity)
    # length = 0.01

    task_data = {
        "item_id": requested_rune.id,
        "num": number,
        "length": length,
        "is_pure": pure
    }

    task = Task(type="runecraft",
                user=user,
                completion_time=utils.command_helpers.calculate_finish_time_utc(length * 60),
                guild=ctx.guild.id,
                channel=ctx.channel.id,
                extra_data=json.dumps(task_data))
    try:
        task.save()
    except Exception as e:
        logging.getLogger(__name__).error("unable to persist task. error: %s", str(e))
        out.description += "Database error trying to start runecrafting session. Please report this in " \
                           "<#981349203395641364>" # This points to #bugs
        return out

    out.description += f"You have started crafting {requested_rune.pluralize(number)} for {length} minutes"
    return out


def start_runecraft(guildid, channelid, user: User, entered_item, number=1, pure=0):
    """Starts a runecrafting session."""

    out = ''
    if not adv.is_on_adventure(user.id):
        item: Item = Item.find_by_name_or_nick(entered_item)
        if not item:
            return f'{entered_item} is not an item.'

        try:
            number = int(number)
        except ValueError:
            return f'{number} is not a valid number.'

        if not item.is_rune:
            return f'{item.name} is not a rune that can be crafted.'

        # Find out if user has the talisman
        rune_type = item.name.split(" ")[0]
        if not user.has_item_by_name(rune_type + " talisman"):
            return f'{rune_type} talisman not found in inventory.'

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

        rc_session = utils.command_helpers.format_adventure_line(6, user.id, utils.command_helpers.calculate_finish_time(length * 60), guildid, channelid,
                                                                 item.id, item_name, number, length, pure)
        adv.write(rc_session)
        out += f'You are now crafting {item.pluralize(number)} for {length} minutes.'
    else:
        out = adv.print_adventure(user.id)
        out += utils.command_helpers.print_on_adventure_error('runecrafting session')
    return out


def list_runes():
    content = [["RUNE", "LEVEL"]]

    for rune in RUNES:
        content.append([rune.name, str(rune.level)])

    return Embed(
        title="Craftable Runes",
        type="rich",
        description=utils.command_helpers.format_as_table(content),
    )
