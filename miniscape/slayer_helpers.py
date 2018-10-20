import logging

from discord import Member

from miniscape.item_helpers import get_loot_value
from miniscape.models import User, Monster, PlayerMonsterKills, Item
from miniscape import adventures as adv
from config import XP_FACTOR
import miniscape.monster_helpers as mon
import miniscape.prayer_helpers as prayer
import math
import random

LOWEST_NUM_TO_KILL = 35

SLAYER_HEADER = ':skull_crossbones: __**SLAYER**__ :skull_crossbones:\n'


def calc_chance(user: User, monster: Monster, number: int, remove_food=False):
    """Calculates the chance of success of a task."""  
    equipment = user.equipment_slots
    player_arm = user.armour
    monster_acc = monster.accuracy
    monster_dam = monster.damage
    monster_combat = monster.level
    player_combat = user.combat_level
    number = int(number)
    monsters_fought = user.monster_kills(monster.name)

    if monsters_fought:
        monsters_fought = monsters_fought[0]
        chance_bonus = 20 * min(monsters_fought.amount / 5000, 1)
    else:
        chance_bonus = 0

    prayer_chance = 0
    if user.prayer_slot is not None:
        player_dam, player_acc, player_arm = prayer.calc_pray_bonus(user)
        if 10 <= int(user.prayer_slot.id) <= 12:
            monster_affinity = monster.affinity
            if monster_affinity == 0 and user.prayer_slot.id == '12' or monster_affinity == 1 and user.prayer_slot.id == '11' \
                    or monster_affinity == 2 and user.prayer_slot.id == '10':
                prayer_chance = user.prayer_slot.chance

    if monster.is_dragon:
        if equipment[6].id in ['266', '293']:
            monster_base = 1
        else:
            monster_base = 100
    elif monster.id == '87':
        if equipment[4].id == '578':
            monster_base = 1
        else:
            monster_base = 100
    else:
        monster_base = 1

    player_potion = equipment[14]
    if player_potion is not None:
        player_potion = player_potion.id
        if player_potion == '429' or player_potion == '430':
            player_arm = player_arm * 1.1 + 3
        if player_potion == '433' or player_potion == '434':
            player_arm = player_arm * 1.15 + 5

    c = 1 + monster_combat / 200
    d = 1 + player_combat / 99
    dam_multiplier = monster_base + monster_acc / 200
    chance = (200 * d * player_arm) / (number / 50 * monster_dam * dam_multiplier + c) + chance_bonus
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


# TODO: calc_length and calc_chance (and also calc_number) use a fuckton of the same code. can we DRY this up?
def calc_length(user: User, monster: Monster, number):
    """Calculates the length of a task."""
    user_prayer = user.prayer_slot
    combat_level = user.combat_level
    equipment = user.equipment_slots
    player_dam, player_acc, player_arm, player_pray = user.equipment_stats
    monster_arm = monster.armour
    monster_xp = monster.xp
    monsters_fought = user.monster_kills(monster.name)
    if monsters_fought:
        monsters_fought = monsters_fought[0]
        time_bonus = 1 - 0.2 * min(monsters_fought.amount / 5000, 1)
    else:
        time_bonus = 1

    if user_prayer is not None:
        player_dam, player_acc, player_arm = prayer.calc_pray_bonus(user)

    if monster.is_dragon:
        if equipment[6].id in ['266', '293']:
            monster_base = 1
        else:
            monster_base = 100
    elif monster.id == '87':
        if equipment[4].id == '578':
            monster_base = 1
        else:
            monster_base = 100
    else:
        monster_base = 1

    player_potion = equipment[14]
    if player_potion:
        player_potion = player_potion.id
        if player_potion == '427' or player_potion == '430':
            player_acc = player_acc * 1.1 + 3
        if player_potion == '428' or player_potion == '430':
            player_dam = player_dam * 1.1 + 3
        if player_potion == '429' or player_potion == '430':
            player_arm = player_arm * 1.1 + 3
        if player_potion == '431' or player_potion == '434':
            player_acc = player_acc * 1.15 + 5
        if player_potion == '432' or player_potion == '434':
            player_dam = player_dam * 1.15 + 5
        if player_potion == '433' or player_potion == '434':
            player_arm = player_arm * 1.15 + 5

    dam_multiplier = 1 + player_acc / 200
    base_time = math.floor(number * monster_xp / 10) * time_bonus
    time = round(base_time * monster_arm * monster_base / (player_dam * dam_multiplier + combat_level))

    return base_time, time


def calc_number(user: User, monster: Monster, time):
    """Calculates the number of monsters that can be killed in a given time period."""
    combat_level = user.combat_level
    equipment = user.equipment_slots
    player_dam, player_acc, player_arm, player_pray = user.equipment_stats
    monster_arm = monster.armour
    monster_xp = monster.xp

    if user.prayer_slot is not None:
        player_dam, player_acc, player_arm = prayer.calc_pray_bonus(user)

    if monster.is_dragon:
        if equipment[6].id in ['266', '293']:
            monster_base = 1
        else:
            monster_base = 100
    elif monster.id == '87':  # Vampyre
        if equipment[4].id == '578':
            monster_base = 1
        else:
            monster_base = 100
    else:
        monster_base = 1

    player_potion = equipment[14]
    if player_potion:
        player_potion = player_potion.id
        if player_potion == '427' or player_potion == '430':
            player_acc = player_acc * 1.1 + 3
        if player_potion == '428' or player_potion == '430':
            player_dam = player_dam * 1.1 + 3
        if player_potion == '429' or player_potion == '430':
            player_arm = player_arm * 1.1 + 3
        if player_potion == '431' or player_potion == '434':
            player_acc = player_acc * 1.15 + 5
        if player_potion == '432' or player_potion == '434':
            player_dam = player_dam * 1.15 + 5
        if player_potion == '433' or player_potion == '434':
            player_arm = player_arm * 1.15 + 5

    dam_multiplier = 1 + player_acc / 200

    number = math.floor((10 * time * (player_dam * dam_multiplier + combat_level)) /
                        (monster_arm * monster_base * monster_xp))
    if number < 0:
        number = 0
    return number


def get_task_info(userid):
    """Gets the info associated with a user's slayer task and returns it as a tuple."""
    task = adv.read(userid)
    taskid, userid, finish_time, guildid, channelid, monsterid, monster_name, num_to_kill, chance = task

    time_left = adv.get_delta(finish_time)

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
        completed_quests = set(author.completed_quests.all())
        equipment = author.equipment_slots

        for _ in range(1000):
            monster = mon.get_random(author, wants_boss=False)

            num_to_kill = random.randint(LOWEST_NUM_TO_KILL, LOWEST_NUM_TO_KILL + 15 + 3 * slayer_level)
            base_time, task_length = calc_length(author, monster, num_to_kill)
            chance = calc_chance(author, monster, num_to_kill)

            mon_level = monster.level
            if 0.25 <= task_length / base_time <= 2 \
                    and chance >= 20 \
                    and mon_level / cb_level >= 0.8 \
                    and task_length <= 3600 \
                    and (monster.quest_req and monster.quest_req in completed_quests):
                break
            else:
                log_str = f"Failed to give task to user\n" \
                          f"User: {author.name}, Monster: {monster.name}\n" \
                          f"Conditionals: \n" \
                          f"  task_length / base_time: {task_length / base_time}\n" \
                          f"  chance: {chance}\n"\
                          f"  mon levl / cb lvl: {mon_level / cb_level}\n" \
                          f"  quest req satisfied: {monster.quest_req and monster.quest_req in completed_quests}\n"
                logging.getLogger(__name__).info(log_str)
                continue  # For breakpoints :^)
        else:
            return "Error: gear too low to fight any monsters. Please equip some better gear and try again. " \
                   "If you are new, type `~starter` to get a bronze kit."
        cb_perk = False
        if author.combat_level == 99 and random.randint(1, 20) == 1:
            task_length *= 0.7
            cb_perk = True

        task = adv.format_line(0, author.id, adv.get_finish_time(task_length), guildid, channelid, monster.id,
                               monster.name, num_to_kill, chance)
        adv.write(task)
        out += print_task(author.id)
        if cb_perk is True:
            out += 'Your time has been reduced by 30% due to your combat perk!'
    else:
        out = adv.print_adventure(author.id)
        out += adv.print_on_adventure_error('task')
    return out


def get_kill(guildid, channelid, userid, monster, length=-1, number=-1):
    """Lets the user start killing monsters.."""
    out = f'{SLAYER_HEADER}'
    user = User.objects.get(id=userid)
    monster = Monster.find_by_name_or_nick(monster)

    if not monster:
        return f'Error: {monster} is not a monster.'

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

        grind = adv.format_line(1, userid, adv.get_finish_time(length * 60), guildid, channelid,
                                monster.id, monster_name, number, length, chance)
        adv.write(grind)
        out += f'You are now killing {monster.pluralize(number, with_zero=True)} for {length} minutes. ' \
               f'You have a {chance}% chance of successfully killing this many monsters without dying.'
    else:
        out = adv.print_adventure(userid)
        out += adv.print_on_adventure_error('kill')
    return out


def get_kill_result(person, *args):
    """Determines the loot of a monster grind."""
    try:
        monsterid, monster_name, num_to_kill, length, chance = args[0]
    except ValueError as e:
        print(e)
        raise ValueError
    num_to_kill = int(num_to_kill)
    user = User.objects.get(id=person.id)
    monster = Monster.objects.get(id=monsterid)
    user.add_kills(monster, num_to_kill)

    chance = calc_chance(user, monster, num_to_kill, remove_food=True)
    is_success = adv.is_success(chance)
    if not is_success and user.prayer_slot.id == '16' and random.randint(0, 1):
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


def print_loot(loot, person: Member, monster: Monster, num_to_kill: int, add_mention=True):
    """Converts a user's loot from a slayer task to a string."""
    out = f'{SLAYER_HEADER}**'
    if add_mention:
        out += f'{person.mention}, '
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
    user: User = User.objects.get(id=person.id)
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
    user: User = User.objects.get(id=person.id)
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

        task_length=0
        task = adv.format_line(5, userid, adv.get_finish_time(task_length), guildid, channelid, monster.id,
                               monster.name, num_to_kill, chance)
        adv.write(task)
        out += print_task(userid, reaper=True)
        if cb_perk:
            out += 'Your time has been reduced by 30% due to your combat perk!'
    else:
        out = adv.print_adventure(userid)
        out += adv.print_on_adventure_error('reaper task')
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
    time_left = adv.get_delta(finish_time)
    return taskid, userid, time_left, monsterid, monster_name, num_to_kill, chance


def print_chance(userid, monsterid, monster_dam=-1, monster_acc=-1, monster_arm=-1, monster_combat=-1, xp=-1,
                 number=100, dragonfire=False):
    user = User.objects.get(id=userid)
    monster = Monster.objects.get(monsterid)
    player_dam, player_acc, player_arm, player_pray = user.equipment_stats

    player_combat = user.combat_level
    if monster_dam == -1:
        monster_dam = monster.damage
        monster_acc = monster.accuracy
        monster_arm = monster.armour
        xp = monster.xp
        monster_combat = monster.level
    if dragonfire:
        monster_base = 100
    else:
        monster_base = 1

    c = 1 + monster_combat / 200
    d = 1 + player_combat / 99
    dam_multiplier = monster_base + monster_acc / 200
    chance = round(min(100 * max(0, (2 * d * player_arm) / (number / 50 * monster_dam * dam_multiplier + c)), 100))

    dam_multiplier = 1 + player_acc / 200
    base_time = math.floor(number * xp / 10)
    time = round(base_time * (monster_arm * monster_base / (player_dam * dam_multiplier + player_combat)))
    out = f'level {monster_combat} monster with {monster_dam} dam {monster_acc} acc {monster_arm} arm giving {xp} xp: ' \
          f'chance: {chance}%, base time: {base_time}, time to kill {number}: {time}, time ratio: {time / base_time}.'
    return out


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
