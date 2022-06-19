import json
import logging

import discord

import utils.command_helpers
from mbot import MiniscapeBotContext
from miniscape.models import User, Quest, Item, Monster, Recipe, UserQuest, Task
from miniscape import adventures as adv
from django.core.exceptions import ObjectDoesNotExist
import string
import math

QUEST_HEADER = ':crossed_swords: __**QUESTS**__ :shield:\n'
DFS = Item.objects.get(name__iexact="dragonfire shield")
ANTI_DRAGON_SHIELD = Item.objects.get(name__iexact="anti-dragon shield")


def calc_chance(user: User, quest, remove_food=False):
    """Calculates the chance of success of a quest."""
    if isinstance(user, str) or isinstance(user, int):
        user = User.objects.get(id=user)
    if isinstance(quest, str) or isinstance(quest, int):
        quest = Quest.objects.get(id=quest)
    # user_prayer = users.read_user(userid, key=users.PRAY_KEY)
    player_arm = user.armour
    player_combat = user.combat_level
    monster_dam, monster_acc, _, monster_combat = quest.combat_stats

    monster_base = 1
    if quest.has_dragon and not(user.has_item_by_item(DFS)
                                or user.has_item_by_item(ANTI_DRAGON_SHIELD)):
            monster_base = 100

    c = 1 + monster_combat / 200
    d = player_combat / 200
    dam_multiplier = monster_base + monster_acc / 200

    chance = 100 * (2 * d * player_arm) / (monster_dam * dam_multiplier + c)

    player_food: Item = user.active_food
    if player_food:
        food_bonus = player_food.food_value
        number = monster_combat / 100
        if food_bonus > 0:
            if user.has_item_amount_by_item(player_food, number):
                chance += food_bonus
            else:
                num_food = user.get_item_count(item=player_food)
                chance +=  int(food_bonus * num_food / number)
                if remove_food:
                    user.update_inventory(player_food, num_food)

    if chance > 100 or monster_dam == 1:
        chance = 100
    if chance < 0:
        chance = 0
    return round(chance)


def calc_length(user, quest):
    """Calculates the length of success of a quest."""
    combat_level = user.combat_level
    # TODO(mitch): Use prayer here
    player_dam, player_acc, player_arm, _ = user.equipment_stats
    monster_arm = quest.armour
    base_time = 60 * quest.time
    monster_base = 1

    if quest.has_dragon and not (user.has_item_by_item(DFS)
                                 or user.has_item_by_item(ANTI_DRAGON_SHIELD)):
        monster_base = 100

    c = combat_level
    dam_multiplier = 1 + player_acc / 200
    time = round(base_time * (monster_arm * monster_base / (player_dam * dam_multiplier + c)))
    if time < 0.5 * base_time:
        time = round(0.5 * base_time)
    if time > 2 * base_time:
        time = 2 * base_time
    return time


def print_quest(quest: Quest, time: int, chance: int):
    """Prints the quest information into a string."""
    out = f"You are now doing the quest {quest.name}. This will take {math.floor(time / 60)} minutes " \
          f"and has a {chance}% chance of succeeding with your current gear. "
    return out


def print_details(user, questid):
    """Prints the details of a quest."""
    try:
        quest = Quest.objects.get(id=questid)
    except ObjectDoesNotExist:
        return f'Error: There is no quest with number {questid}.'

    out = f'{QUEST_HEADER}'
    out += f'**{quest.id}: {quest.name}**\n'
    out += f'*{quest.description}*\n\n'

    out += f'**Base Time**: {quest.time} minutes.\n'

    if user.has_completed_quest(quest):
        out += f'\n*{quest.success}*\n'

    quest_reqs = quest.quest_reqs.all()
    if len(quest_reqs) > 0:
        out += f'\n**Quest Requirements**:\n'
        for quest_req in quest_reqs:
            if user.has_completed_quest(quest_req):
                out += f'~~{quest_req.id}. {quest_req.name}~~\n'
            else:
                out += f'{quest_req.id}. {quest_req.name}\n'

    item_reqs = quest.required_items
    if len(item_reqs) > 0:
        out += f'\n**Item Requirements**:\n'
        for qir in item_reqs:
            if user.has_item_amount_by_item(qir.item, qir.amount):
                out += f'~~{ qir.item.pluralize(qir.amount)}~~\n'
            else:
                out += f'{qir.item.pluralize(qir.amount)}\n'

    out += f'\nIf you would like to do this quest, type `~quest start {questid}`.'
    return out


def print_status2(task: Task, time_left):
    extra_data = json.loads(task.extra_data)
    quest = Quest.objects.get(id=extra_data["quest_id"])
    chance = extra_data["chance"]
    return f"{QUEST_HEADER}"\
           f"You are on the quest {quest.name}. You can see the results of this in {time_left} minutes. "\
           f"You currently have a {chance}% of succeeding with your current gear. "


def print_status(userid, time_left, *args):
    questid, chance = args[0]
    quest = Quest.objects.get(id=questid)
    chance = calc_chance(userid, questid)
    out = f'{QUEST_HEADER}' \
          f'You are already on the quest {quest.name}. You can see the results of this quest {time_left}. ' \
          f'You currently have a {chance}% of succeeding with your current gear. '
    return out


def start_quest(ctx: MiniscapeBotContext, questid):
    """Assigns a user a slayer task provided they are not in the middle of another adventure."""
    out = discord.Embed(type="rich", title="Quest", description=QUEST_HEADER)
    user = ctx.user_object

    if adv.is_on_adventure(user.id):
        out.description = adv.print_adventure(user.id)
        out.description += utils.command_helpers.print_on_adventure_error('quest')
        return out

    try:
        quest = Quest.objects.get(id=questid)
    except ObjectDoesNotExist:
        out.description += f"Error: quest number {questid} does not refer to any quest."
        return out

    if quest in user.completed_quests_list:
        out.description += "Error: you have already done this quest."
        return out

    if not user.has_quest_req_for_quest(quest):
        out.description += "Error: you have not completed the required quests to do this quest."
        return out

    if not user.has_items_for_quest(quest):
        out.description += "Error: you do not have all the required items to start this quest."
        return out

    chance = calc_chance(user, quest)
    quest_length = calc_length(user, quest)
    task_data = {"quest_id": questid, "chance": chance}
    task = Task(
        type="quest",
        user=user,
        completion_time=utils.command_helpers.calculate_finish_time_utc(quest_length),
        guild=ctx.guild.id,
        channel=ctx.channel.id,
        extra_data=json.dumps(task_data)
    )
    try:
        task.save()
    except Exception as e:
        logging.getLogger(__name__).error("unable to persist task. error: %s", str(e))
        out.description += "Database error trying to start quest. Please report this in " \
                           "<#981349203395641364>"  # This points to #bugs
        return out

    out.description += print_quest(quest, quest_length, chance)
    return out


def get_quest_result(task: Task):
    # Extract our data
    extra_data = json.loads(task.extra_data)
    quest_id = extra_data["quest_id"]
    quest = Quest.objects.get(id=quest_id)
    chance = extra_data["chance"]
    user = task.user

    # Create our return message
    out = discord.Embed(title=QUEST_HEADER, description="", type="rich")
    out.description = f"**{task.user.mention}, here is the result of your quest: {quest.name}**\n"

    # Did they fail?
    if not adv.is_success(chance):
        out.description += f'*{quest.failure}*'
    else:
        out.description += f'*{quest.success}*\n\n'

        # Give the user their reward items
        reward = quest.reward_items
        if reward:
            out.description += f'**Reward**:\n'

            loot = {}
            for qir in reward:
                loot[qir.item] = qir.amount
                out.description += f'{qir.amount} {qir.item.name}\n'
            user.update_inventory(loot)
            out.description += '\n'

        # tell the user what items they've now unlocked
        quest_items = Item.objects.filter(quest_req=quest)
        if quest_items:
            out.description += f'**You Can Now Use**:\n'
            for item in quest_items:
                out.description += f'{string.capwords(item.name)}\n'
            out.description += '\n'

        # tell the user what recipes they've now unlocked
        quest_recipes = Recipe.objects.filter(quest_requirement=quest)
        if quest_recipes:
            out.description += f'**You Can Now Craft**:\n'
            for qr in quest_recipes:
                out.description += f'{qr.creates.name}\n'
            out.description += '\n'

        # tell the user what monsters they've now unlocked
        quest_monsters = Monster.objects.filter(quest_req=quest)
        if quest_monsters:
            out.description += f'**You Can Now Fight**:\n'
            for monster in quest_monsters:
                out.description += f'{monster.name}\n'
            out.description += '\n'

        uq = UserQuest(user=user, quest=quest)
        uq.save()
    return out


def get_result(person, *args):
    """Gets the result of a quest."""

    try:
        questid, chance = args[0]
    except ValueError as e:
        print(e)
        raise ValueError

    user: User = User.objects.get(id=person)
    quest: Quest = Quest.objects.get(id=questid)

    out = f'{QUEST_HEADER}**<@{person}>, here is the result of your quest, {quest.name}**:\n'
    if adv.is_success(calc_chance(user, quest, remove_food=True)):
        out += f'*{quest.success}*\n\n'

        reward = quest.reward_items
        if reward:
            out += f'**Reward**:\n'

            loot = {}
            for qir in reward:
                loot[qir.item] = qir.amount
                out += f'{qir.amount} {qir.item.name}\n'
            user.update_inventory(loot)
            out += '\n'

        quest_items = Item.objects.filter(quest_req__id=questid)
        if quest_items:
            out += f'**You Can Now Use**:\n'
            for item in quest_items:
                out += f'{string.capwords(item.name)}\n'
            out += '\n'

        quest_recipes = Recipe.objects.filter(quest_requirement__id=questid)
        if quest_recipes:
            out += f'**You Can Now Craft**:\n'
            for qr in quest_recipes:
                out += f'{qr.creates.name}\n'
            out += '\n'

        quest_monsters = Monster.objects.filter(quest_req_id=questid)
        if quest_monsters:
            out += f'**You Can Now Fight**:\n'
            for monster in quest_monsters:
                out += f'{monster.name}\n'
            out += '\n'

        uq = UserQuest(user=user, quest=quest)
        uq.save()
    else:
        out += f'*{quest.failure}*'
    return out


def print_list(user, incomplete=False, search="", get_stats=True, allow_empty=True, ignore_req=False):
    """Lists quests a user can do at the moment."""
    out = f'{QUEST_HEADER}'
    messages = []
    all_quests = Quest.objects.filter(name__icontains=search)

    if not all_quests and not allow_empty:
        return []

    user_quests = user.completed_quests_list

    for quest in all_quests:
        if quest in user_quests:
            if incomplete:
                continue  # Skip because only showing incomplete ones
            out += f'~~**{quest.id}**. {quest.name}~~\n'
        elif user.has_quest_req_for_quest(quest, user_quests) or ignore_req:
            out += f'**{quest.id}**. {quest.name}\n'

        if len(out) > 1800:
            messages.append(out)
            out = f'{QUEST_HEADER}'

    if get_stats:
        out += f'\n**Quests Completed**: {user.num_quests_complete}/{Quest.objects.count()}\n'
    out += 'Type `~quest [quest number]` to see more information about a quest.\n'
    messages.append(out)
    return messages
