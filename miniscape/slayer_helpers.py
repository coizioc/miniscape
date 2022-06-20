import json
import logging

import discord
from discord import Member

import utils.command_helpers
from utils.command_helpers import truncate_task
from mbot import MiniscapeBotContext
from miniscape.item_helpers import get_loot_value
from miniscape.itemconsts import SLAYER_HELMET
from miniscape.models import User, Monster, PlayerMonsterKills, Item, Task, Prayer
from miniscape import adventures as adv
from config import XP_FACTOR
import miniscape.monster_helpers as mon
import miniscape.prayer_helpers as prayer
import math
import random

LOWEST_NUM_TO_KILL = 35

SLAYER_HEADER = ':skull_crossbones: __**SLAYER**__ :skull_crossbones:\n'
PROTECT_ITEM = Prayer.objects.get(name__iexact="protect item")


def calc_chance(user: User, monster: Monster, number: int, remove_food=False):
    """Calculates the chance of success of a task."""
    number = int(number)

    player_dam, player_acc, player_arm, dam_multiplier, monster_base, chance_bonus = calc_task_vars(user, monster)

    prayer_chance = 0
    if user.prayer_slot is not None:
        if 10 <= user.prayer_slot.id <= 12:   # if user is using protect from mage/range/melee
            monster_affinity = monster.affinity
            if monster_affinity == 0 and user.prayer_slot.id == 12\
                    or monster_affinity == 1 and user.prayer_slot.id == 11 \
                    or monster_affinity == 2 and user.prayer_slot.id == 10:
                prayer_chance = user.prayer_slot.chance

    chance = (200 * (1 + user.combat_level / 99) * player_arm) /\
             (number / 50 * monster.damage * dam_multiplier + (1 + monster.level / 200)) + chance_bonus

    if user.equipment_slots[0] == SLAYER_HELMET:
        chance = min(round(chance * 1.125), 100)

    if user.is_eating:
        food_bonus = user.active_food.food_value
        if food_bonus > 0:
            num_food = user.get_item_by_item(user.active_food)
            if num_food:
                num_food = num_food[0].amount
                chance += food_bonus if num_food >= number else int(food_bonus * num_food / number)
                amount = number if num_food >= number else num_food
                if remove_food:
                    user.update_inventory({user.active_food.id: amount}, remove=True)
            else:
                user.active_food = None
                user.save()

    chance += prayer_chance

    if chance > 100:
        chance = 100
    if chance < 0:
        chance = 0
    return round(chance)


def calc_length(user: User, monster: Monster, number):
    """Calculates the length of a task."""
    player_dam, player_acc, player_arm, dam_multiplier, monster_base, time_bonus = calc_task_vars(user, monster)

    base_time = math.floor(number * monster.xp / 10) * time_bonus
    time = round(base_time * monster.armour * monster_base / (player_dam * dam_multiplier + user.combat_level))

    if time < 0:
        time = 0
    return base_time, time


def calc_monster_base(user: User, monster: Monster):
    """Calculates the monster_base for a given user and monster."""
    equipment = user.equipment_slots
    # If off-hand is anti-dragon shield or dragonfire shield.
    if monster.is_dragon:
        if equipment[6].id in [266, 293]:
            monster_base = 1
        else:
            monster_base = 100
    # if monster is a vampyre whether the user is wielding an Ivandis flail.
    elif monster.id == 87:
        if equipment[4].id == 578:
            monster_base = 1
        else:
            monster_base = 100
    else:
        monster_base = 1
    return monster_base


def calc_number(user: User, monster: Monster, time):
    """Calculates the number of monsters that can be killed in a given time period."""
    player_dam, player_acc, player_arm, dam_multiplier, monster_base, time_bonus = calc_task_vars(user, monster)

    number = math.floor((10 * time * (player_dam * dam_multiplier + user.combat_level)) /
                        (monster.armour * monster_base * monster.xp))
    if number < 0:
        number = 0
    return number


def calc_task_vars(user: User, monster: Monster):
    """Calculates the variables required to calculate a task's length/number."""
    user_prayer = user.prayer_slot
    equipment = user.equipment_slots
    player_dam, player_acc, player_arm, _ = user.equipment_stats
    monsters_fought = user.monster_kills(monster.name)
    if monsters_fought:
        monsters_fought = monsters_fought[0]
        monster_num_bonus = 1 - 0.2 * min(monsters_fought.amount / 5000, 1)
    else:
        monster_num_bonus = 1

    if user_prayer is not None:
        player_dam, player_acc, player_arm = prayer.calc_pray_bonus(user)

    monster_base = calc_monster_base(user, monster)

    player_potion = equipment[14]
    if player_potion:
        player_potion = player_potion.id
        if player_potion == 427 or player_potion == 430:
            player_acc = player_acc * 1.1 + 3
        if player_potion == 428 or player_potion == 430:
            player_dam = player_dam * 1.1 + 3
        if player_potion == 429 or player_potion == 430:
            player_arm = player_arm * 1.1 + 3
        if player_potion == 431 or player_potion == 434:
            player_acc = player_acc * 1.15 + 5
        if player_potion == 432 or player_potion == 434:
            player_dam = player_dam * 1.15 + 5
        if player_potion == 433 or player_potion == 434:
            player_arm = player_arm * 1.15 + 5

    dam_multiplier = 1 + player_acc / 200
    return tuple((player_dam, player_acc, player_arm, dam_multiplier, monster_base, monster_num_bonus))


def get_task_info(userid):
    """Gets the info associated with a user's slayer task and returns it as a tuple."""
    task = adv.read(userid)
    taskid, userid, finish_time, guildid, channelid, monsterid, monster_name, num_to_kill, chance = task

    time_left = utils.command_helpers.get_delta(finish_time)

    return taskid, userid, time_left, monsterid, monster_name, num_to_kill, chance


def print_task(userid, reaper=False):
    """Converts a user's task into a string."""
    taskid, userid, task_length, monsterid, monster_name, num_to_kill, chance = get_task_info(userid)
    if reaper:
        out = f'New reaper task received: '
    else:
        out = f'New slayer task received: '
    num_to_kill = int(num_to_kill)
    monster = Monster.objects.get(id=monsterid)
    out += f'Kill __{monster.pluralize(num_to_kill)}__!\n'
    out += f'This will take {task_length} minutes '
    out += f'and has a success rate of {chance}% with your current gear. '
    return out


def get_task(guildid, channelid, author: User):
    """Assigns a user a slayer task provided they are not in the middle of another adventure."""
    out = SLAYER_HEADER

    if not adv.is_on_adventure(author.id):
        cb_level = author.combat_level
        slayer_level = author.slayer_level

        for _ in range(1000):
            monster = mon.get_random(author, wants_boss=False)
            min_assign = monster.min_assignable
            num_to_kill = random.randint(min_assign, min_assign + 15 + 3 * slayer_level)
            base_time, task_length = calc_length(author, monster, num_to_kill)
            chance = calc_chance(author, monster, num_to_kill)

            mon_level = monster.level
            #if 0.25 <= task_length / base_time <= 2 \
            if 600 <= task_length  \
                    and chance >= 20 \
                    and mon_level / cb_level >= 0.8 \
                    and task_length <= 3600:
                break
            else:
                log_str = f"Failed to give task to user\n" \
                          f"User: {author.name}, Monster: {monster.name}\n" \
                          f"Conditionals: \n" \
                          f"  num to kill: {num_to_kill}\n" \
                          f"  task_length / base_time: {task_length / base_time}\n" \
                          f"  chance: {chance}\n"\
                          f"  mon levl / cb lvl: {mon_level / cb_level}\n"
                logging.getLogger(__name__).info(log_str)
                continue  # For breakpoints :^)
        else:
            return "Error: gear too low to fight any monsters. Please equip some better gear and try again. " \
                   "If you are new, type `~starter` to get a bronze kit."
        cb_perk = False
        if author.combat_level == 99 and random.randint(1, 20) == 1:
            task_length *= 0.7
            cb_perk = True

        task = utils.command_helpers.format_adventure_line(0, author.id, utils.command_helpers.calculate_finish_time(task_length), guildid, channelid, monster.id,
                                                           monster.name, num_to_kill, chance)
        adv.write(task)
        out += print_task(author.id)
        if cb_perk is True:
            out += 'Your time has been reduced by 30% due to your combat perk!'
    else:
        out = adv.print_adventure(author.id)
        out += utils.command_helpers.print_on_adventure_error('task')
    return out


def start_kill(ctx: MiniscapeBotContext, monster_name, length=0, number=0):
    out = discord.Embed(title=SLAYER_HEADER, type="rich", description="")
    user = ctx.user_object

    # Are they already on an adventure?
    if adv.is_on_adventure(ctx.user_object.id):
        out.description += adv.print_adventure(ctx.user_object.id)
        out.description += utils.command_helpers.print_on_adventure_error('kill')
        return out

    # Does the monster they requested actually exist?
    monster = Monster.find_by_name_or_nick(monster_name)
    if not monster:
        out.description += f"Error: {monster_name} is not a monster"
        return out

    # Do they have the quest requirement to access it?
    if monster.quest_req and not user.has_completed_quest(monster.quest_req):
        out.description += f"You do not have the required quest ({monster.quest_req.name}) to kill this monster"
        return out

    # Do they have the slayer level for it?
    if user.slayer_level < monster.slayer_level_req:
        out.description += f"Error: {monster.name} has a slayer requirement ({monster.slayer_level_req}) higher" \
                           f"than your slayer level ({user.slayer_level})"
        return out

    # Validate they sent us numbers for these
    try:
        number = int(number)
        length = int(length)
    except ValueError:
        out.description += f"Error: Neither length nor number provided to start_kill. " \
                           f"Please report this in <#981349203395641364>"
        return out

    # Did they request a number to kill? e.g. ~kill <NUMBER> <MONSTER>
    # or did they request a length? e.g. ~kill <MONSTER> <LENGTH>
    # First branch is for number, elif is for length
    if number > 0:
        truncated_num, truncated = truncate_task(user.slayer_level, number)
        if truncated:
            out.description += f"Kill request truncated from {number} to {truncated_num}\n\n"
        number = truncated_num
        base_time, time = calc_length(user, monster, number)
        length = math.floor(time / 60)
    elif length > 0:
        # Truncate the length if they requested more than they're allowed
        if length > 180:
            out.description += f"Kill duration requested truncated from {length} to 180 mins\n"
            length = 180

        number = calc_number(user, monster, (length+1)*60) - 1
        truncated_num, truncated = truncate_task(user.slayer_level, number)
        if truncated:
            out.description += f"Kill request truncated from {number} to {truncated_num}\n\n"
        number = truncated_num
    else:
        out.description += f"Error: Argument missing"
        return out

    # What's our chance of killing this many mobs?
    chance = calc_chance(user, monster, number)

    extra_data = {
        "monster_id": monster.id,
        "monster_name": monster.name,
        "number": number,
        "length": length,
        "chance": chance,
    }
    task = Task(
        type="kill",
        user=user,
        completion_time=utils.command_helpers.calculate_finish_time_utc(length*60),
        guild=ctx.guild.id,
        channel=ctx.channel.id,
        extra_data=json.dumps(extra_data)
    )
    task.save()
    out.description += f"You are now killing {monster.pluralize(number)} for {length} minutes. " \
                       f"You have a {chance}% chance of successfully killing this many monsters without dying."
    return out


def get_kill(guildid, channelid, userid, monstername, length=-1, number=-1):
    """Lets the user start killing monsters.."""
    out = f'{SLAYER_HEADER}'
    user = User.objects.get(id=userid)
    monster = Monster.find_by_name_or_nick(monstername)

    if not monster:
        return f'Error: {monstername} is not a monster.'

    completed_quests = set(user.completed_quests.all())
    if monster.quest_req and monster.quest_req not in completed_quests:
        return f'Error: you do not have the required quests to kill this monster.'

    try:
        length = int(length)
        number = int(number)
    except ValueError:
        return f'Error: {length} is not a valid length of time.'

    if not adv.is_on_adventure(user.id):
        monster_name = monster.name
        if user.slayer_level < monster.slayer_level_req:
            return f'Error: {monster.name} has a slayer requirement ({monster.slayer_level_req}) higher ' \
                   f'than your slayer level ({user.slayer_level})'
        if number > 1000 and user.slayer_level == 99:
            number = 1000
        if number > 500 and user.slayer_level < 99:
            number = 500
        if length > 180:
            length = 180

        if int(number) < 0:
            number = calc_number(user, monster, (length + 1) * 60) - 1
            if number > 1000 and user.slayer_level == 99:
                number = 1000
            if number > 500 and user.slayer_level < 99:
                number = 500
        elif int(length) < 0:
            length = math.floor(calc_length(user, monster, number)[1] / 60)
        else:
            return 'Error: argument missing (number or kill length).'

        chance = calc_chance(user, monster, number)

        grind = utils.command_helpers.format_adventure_line(1, userid, utils.command_helpers.calculate_finish_time(length * 60), guildid, channelid,
                                                            monster.id, monster_name, number, length, chance)
        adv.write(grind)
        out += f'You are now killing {monster.pluralize(number, with_zero=True)} for {length} minutes. ' \
               f'You have a {chance}% chance of successfully killing this many monsters without dying.'
    else:
        out = adv.print_adventure(userid)
        out += utils.command_helpers.print_on_adventure_error('kill')
    return out


def print_kill_status_new(task: Task, time_left):
    extra_data = json.loads(task.extra_data)
    monster = Monster.objects.get(id=extra_data["monster_id"])
    number = extra_data["number"]
    length = extra_data["length"]
    chance = extra_data["chance"]

    out = f'{SLAYER_HEADER}' \
          f'You are currently killing {monster.pluralize(number, with_zero=True)} for {length} minutes. ' \
          f'You have a {chance}% chance of killing this many monsters without dying. ' \
          f'You can see your loot {time_left} minutes.'
    return out


def get_kill_results(task: Task):
    # Extract info from the task
    extra_data = json.loads(task.extra_data)
    monster_id = extra_data["monster_id"]
    monster = Monster.objects.get(id=monster_id)
    number = int(extra_data["number"])
    chance = int(extra_data["chance"])
    user = task.user

    # Did they die?
    is_success = adv.is_success(chance)
    if not is_success and user.prayer_slot == PROTECT_ITEM and random.randint(0, 1):
        is_success = True

    # Generate loot
    factor = 1 if is_success else int(chance) / 100
    factor *= user.luck_factor
    loot = monster.generate_loot(number, factor)

    # Award loot, kills, xp
    user.add_kills(monster, number)
    user.update_inventory(loot)

    xp_gained = monster.xp * number
    cb_level_before = user.combat_level
    user.combat_xp += xp_gained
    cb_level_after = user.combat_level

    # Tell them what they did
    out = discord.Embed(title=SLAYER_HEADER, type="rich", description="")
    combat_xp_formatted = '{:,}'.format(xp_gained)
    out.description += print_loot(loot, user, monster, number, print_header=False)

    out.description += f'\nYou have also gained {combat_xp_formatted} combat xp'
    if cb_level_after > cb_level_before:
        out.description += f' and {cb_level_after - cb_level_before} combat levels'
    out.description += '.\n'
    if not is_success:
        out.description += f'You have received lower loot and experience because you have died.\n'
    user.potion_slot = None
    user.save()
    return out


def get_kill_result(person, *args):
    """Determines the loot of a monster grind."""
    try:
        monsterid, monster_name, num_to_kill, length, chance = args[0]
    except ValueError as e:
        print(e)
        raise ValueError
    num_to_kill = int(num_to_kill)
    user = User.objects.get(id=person)
    monster = Monster.objects.get(id=monsterid)
    user.add_kills(monster, num_to_kill)

    chance = calc_chance(user, monster, num_to_kill, remove_food=True)
    is_success = adv.is_success(chance)
    if not is_success and user.prayer_slot_id == '16' and random.randint(0, 1):
        is_success = True

    factor = 1 if is_success else int(chance) / 100
    factor *= user.luck_factor

    loot = monster.generate_loot(num_to_kill, factor)
    user.update_inventory(loot)
    out = print_loot(loot, person, monster, num_to_kill)

    xp_gained = monster.xp*num_to_kill
    cb_level_before = user.combat_level
    user.combat_xp += xp_gained
    cb_level_after = user.combat_level
    combat_xp_formatted = '{:,}'.format(xp_gained)

    out += f'\nYou have also gained {combat_xp_formatted} combat xp'
    if cb_level_after > cb_level_before:
        out += f' and {cb_level_after - cb_level_before} combat levels'
    out += '.\n'
    if not is_success:
        out += f'You have received lower loot and experience because you have died.\n'
    user.potion_slot = None
    user.save()
    return out


def print_loot(loot, person, monster: Monster, num_to_kill: int, add_mention=True, print_header=True):
    """Converts a user's loot from a slayer task to a string."""
    if print_header:
        out = f'{SLAYER_HEADER}**'
    else:
        out = "**"

    if type(person) == User:
        if add_mention:
            out += f'{person.mention}, '
        else:
            out += f'{person.name}, '
    else:
        if add_mention:
            out += f'<@{person}>, '
        else:
            out += f'{person.name}, '
    #
    out += f'Your loot from your {monster.pluralize(num_to_kill, with_zero=True)} has arrived!**\n'

    # TODO: Update this to print in order of rarity
    rares = [ml.item for ml in monster.rares]
    for item, amount in loot.items():
        item_name = item.pluralize(amount)
        if item in rares:
            out += f'**{item_name}**\n'
        else:
            out += f'{item_name}\n'
    total_value = '{:,}'.format(get_loot_value(loot))
    out += f'*Total value: {total_value}*'

    return out


def get_result(person, *args):
    """Determines the success and loot of a slayer task."""
    try:
        monsterid, monster_name, num_to_kill, chance = args[0]
    except ValueError as e:
        print(e)
        raise ValueError
    num_to_kill = int(num_to_kill)
    user: User = User.objects.get(id=person)
    monster: Monster = Monster.objects.get(id=monsterid)
    user.add_kills(monster, num_to_kill)

    chance = calc_chance(user, monster, num_to_kill, remove_food=True)
    is_success = adv.is_success(chance)
    factor = 1 if is_success else int(chance) / 100
    factor *= user.luck_factor

    user.potion_slot = None
    loot = monster.generate_loot(num_to_kill, user.luck_factor)
    user.update_inventory(loot)
    out = print_loot(loot, person, monster, num_to_kill)

    xp_gained = round(XP_FACTOR * monster.xp * num_to_kill * factor)
    cb_level_before = user.combat_level
    slay_level_before = user.slayer_level
    user.slayer_xp += xp_gained
    user.combat_xp += round(0.7 * xp_gained)
    cb_level_after = user.combat_level
    slay_level_after = user.slayer_level

    slayer_xp_formatted = '{:,}'.format(xp_gained)
    combat_xp_formatted = '{:,}'.format(round(0.7 * xp_gained))

    if not is_success:
        out += f'\nYou have received lower loot and experience because you have died. '
    out += f'\nYou have gained {slayer_xp_formatted} slayer xp and {combat_xp_formatted} combat xp. '
    if cb_level_after > cb_level_before:
        out += f'In addition, you have gained {cb_level_after - cb_level_before} combat levels. '
    if slay_level_after > slay_level_before:
        out += f'Also, as well, you have gained {slay_level_after - slay_level_before} slayer levels. '

    user.save()
    return out


def get_reaper_result(person, *args):
    """Determines the success and loot of a reaper task."""
    try:
        monsterid, monster_name, num_to_kill, chance = args[0]
    except ValueError as e:
        print(e)
        raise ValueError
    num_to_kill = int(num_to_kill)
    user: User = User.objects.get(id=person)
    monster: Monster = Monster.objects.get(id=monsterid)
    out = ''

    # update some user fields
    user.add_kills(monster, num_to_kill)
    user.is_reaper_complete = True
    user.potion_slot = None

    # Were we successful?
    is_success = adv.is_success(calc_chance(user, monster, num_to_kill))
    factor = (2 * user.luck_factor) if is_success else (chance / 170 * user.luck_factor)
    xp_factor = 1 if is_success else factor

    # Give player their loot
    logging.getLogger(__name__).info("Generating loot for reaper task: %d %s" % (num_to_kill,
                                                                                  monster.name))
    loot = monster.generate_loot(num_to_kill, factor)
    logging.getLogger(__name__).info("Generated loot for reaper task: %s" % loot)
    loot[Item.objects.get(id=291)] += 1
    user.update_inventory(loot)
    out += print_loot(loot, person, monster, num_to_kill)

    # Xp and levels
    xp_gained = round(XP_FACTOR * monster.xp * num_to_kill * xp_factor)
    cb_level_before = user.combat_level
    slay_level_before = user.slayer_level
    user.slayer_xp += xp_gained
    user.combat_xp += round(0.7*xp_gained)
    cb_level_after = user.combat_level
    slay_level_after = user.slayer_level

    # Format the shit for printing
    slayer_xp_formatted = '{:,}'.format(xp_gained)
    combat_xp_formatted = '{:,}'.format(round(0.7 * xp_gained))

    if is_success:
        out += f'\nYou have also gained {slayer_xp_formatted} slayer xp and {combat_xp_formatted} combat xp. '

    else:
        out += f'\nYou have received lower loot and experience because you have died.' \
               f'\nYou have received {slayer_xp_formatted} slayer xp and {combat_xp_formatted} combat xp. '

    if cb_level_after > cb_level_before:
        out += f'In addition, you have gained {cb_level_after - cb_level_before} combat levels. '
    if slay_level_after > slay_level_before:
        out += f'Also, as well, you have gained {slay_level_after - slay_level_before} slayer levels. '

    user.save()
    return out


def get_reaper_task(guildid, channelid, userid):
    """Assigns a user a reaper task provided they are not in the middle of another adventure."""
    out = SLAYER_HEADER
    user: User= User.objects.get(id=userid)
    if user.slayer_level < 50:
        out += "Your slayer level is too low to start a reaper task. You need at least 50 slayer."
        return out
    if user.is_reaper_complete:
        out += 'You have already done a reaper task today. Please come back tomorrow for another one.'
        return out

    if not adv.is_on_adventure(userid):
        completed_quests = set(user.completed_quests.all())
        slayer_level = user.slayer_level
        for _ in range(1000):
            monster = mon.get_random(user, wants_boss=True)
            num_to_kill = random.randint(LOWEST_NUM_TO_KILL, LOWEST_NUM_TO_KILL + 15 + 3 * slayer_level)
            base_time, task_length = calc_length(user, monster, num_to_kill)
            chance = calc_chance(user, monster, num_to_kill)
            # print(f'{monsterid} {task_length/base_time} {chance}')
            if 0.25 <= task_length / base_time <= 2 and chance >= 80 \
                    and (monster.quest_req and monster.quest_req in completed_quests):
                break
        else:
            return "Error: gear too low to fight any monsters. Please equip some better gear and try again. " \
                   "If you are new, type `~starter` to get a bronze kit."

        cb_perk = False
        if user.combat_level == 99 and random.randint(1, 20) == 1:
            task_length *= 0.7
            cb_perk = True

        task = utils.command_helpers.format_adventure_line(5, userid, utils.command_helpers.calculate_finish_time(task_length), guildid, channelid, monster.id,
                                                           monster.name, num_to_kill, chance)
        adv.write(task)
        out += print_task(userid, reaper=True)
        if cb_perk:
            out += 'Your time has been reduced by 30% due to your combat perk!'
    else:
        out = adv.print_adventure(userid)
        out += utils.command_helpers.print_on_adventure_error('reaper task')
    return out


def print_status(userid, time_left, *args):
    monsterid, monster_name, num_to_kill, chance = args[0]
    monster = Monster.objects.get(id=monsterid)
    chance = calc_chance(User.objects.get(id=userid),
                         monster,
                         num_to_kill)
    out = f'{SLAYER_HEADER}' \
          f'You are currently slaying {monster.pluralize(num_to_kill, with_zero=True)}. ' \
          f'You can see the results of this slayer task {time_left}. ' \
          f'You currently have a {chance}% chance of succeeding with your current gear. '
    return out


def print_kill_status(userid, time_left, *args):
    monsterid, monster_name, num_to_kill, length, chance = args[0]
    monster = Monster.objects.get(id=monsterid)
    chance = calc_chance(User.objects.get(id=userid),
                         monster,
                         num_to_kill)
    out = f'{SLAYER_HEADER}' \
          f'You are currently killing {monster.pluralize(num_to_kill, with_zero=True)} for {length} minutes. ' \
          f'You currently have a {chance}% chance of killing this many monsters without dying. ' \
          f'You can see your loot {time_left}.'
    return out


def get_task_info(userid):
    """Gets the info associated with a user's slayer task and returns it as a tuple."""
    task = adv.read(userid)
    taskid, userid, finish_time, guildid, channelid, monsterid, monster_name, num_to_kill, chance = task
    time_left = utils.command_helpers.get_delta(finish_time)
    return taskid, userid, time_left, monsterid, monster_name, num_to_kill, chance


def print_reaper_status(userid, time_left, *args):
    monsterid, monster_name, num_to_kill, chance = args[0]
    user = User.objects.get(id=userid)
    monster = Monster.objects.get(id=monsterid)
    chance = calc_chance(user, monster, num_to_kill)
    out = f'{SLAYER_HEADER}' \
          f'You are currently on a reaper task of {monster.pluralize(num_to_kill, with_zero=True)}. ' \
          f'You can see the results of this slayer task {time_left}. ' \
          f'You currently have a {chance}% chance of succeeding with your current gear. '
    return out


def print_task(userid, reaper=False):
    """Converts a user's task into a string."""
    taskid, userid, task_length, monsterid, monster_name, num_to_kill, chance = get_task_info(userid)
    if reaper:
        out = f'New reaper task received: '
    else:
        out = f'New slayer task received: '
    monster = Monster.objects.get(id=monsterid)
    out += f'Kill __{monster.pluralize(num_to_kill, with_zero=True)}__!\n'
    out += f'This will take {task_length} minutes '
    out += f'and has a success rate of {chance}% with your current gear. '
    return out
