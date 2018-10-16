import math
import random

from miniscape import adventures as adv
from cogs.helper import items
from cogs.helper import monsters as mon
from cogs.helper import prayer
from cogs.helper import users

LOWEST_NUM_TO_KILL = 35
SLAYER_HEADER = ':skull_crossbones: __**SLAYER**__ :skull_crossbones:\n'


def calc_chance(userid, monsterid, number, remove_food=False):
    """Calculates the chance of success of a task."""
    user_prayer = users.read_user(userid, key=users.PRAY_KEY)
    equipment = users.read_user(userid, key=users.EQUIPMENT_KEY)
    player_arm = users.get_equipment_stats(equipment)[2]
    monster_acc = mon.get_attr(monsterid, key=mon.ACCURACY_KEY)
    monster_dam = mon.get_attr(monsterid, key=mon.DAMAGE_KEY)
    monster_combat = mon.get_attr(monsterid, key=mon.LEVEL_KEY)
    player_combat = users.xp_to_level(users.read_user(userid, key=users.SLAYER_XP_KEY))
    number = int(number)
    monsters_fought = users.read_user(userid, key=users.MONSTERS_KEY)
    if monsterid in monsters_fought.keys():
        chance_bonus = 20 * min(monsters_fought[monsterid] / 5000, 1)
    else:
        chance_bonus = 0

    if user_prayer != -1:
        player_dam, player_acc, player_arm = prayer.calc_pray_bonus(userid)

    if mon.get_attr(monsterid, key=mon.DRAGON_KEY):
        if equipment['7'] == '266' or equipment['7'] == '293':
            monster_base = 1
        else:
            monster_base = 100
    else:
        monster_base = 1
    if monsterid == '87':
        if equipment['5'] == '578':
            monster_base = 1
        else:
            monster_base = 100

    player_potion = equipment['15']
    if player_potion == '429' or player_potion == '430':
        player_arm = player_arm * 1.1 + 3
    if player_potion == '433' or player_potion == '434':
        player_arm = player_arm * 1.15 + 5

    c = 1 + monster_combat / 200
    d = 1 + player_combat / 99
    dam_multiplier = monster_base + monster_acc / 200
    chance = (200 * d * player_arm) / (number / 50 * monster_dam * dam_multiplier + c) + chance_bonus
    player_food = users.read_user(userid, key=users.FOOD_KEY)
    if int(player_food) > -1:
        food_bonus = items.get_attr(player_food, key=items.EAT_KEY)
        if food_bonus > 0:
            num_food = users.count_item_in_inventory(userid, player_food)
            chance += food_bonus if num_food >= number else int(food_bonus * num_food / number)
            loot = number * [player_food] if num_food >= number else num_food * [player_food]
            if remove_food:
                users.update_inventory(userid, loot, remove=True)

    if 10 <= int(user_prayer) <= 12:
        monster_affinity = mon.get_attr(monsterid, key=mon.AFFINITY_KEY)
        if monster_affinity == 0 and user_prayer == '12' or monster_affinity == 1 and user_prayer == '11' \
                or monster_affinity == 2 and user_prayer == '10':
            chance += prayer.get_attr(user_prayer, key=prayer.CHANCE_KEY)

    if chance > 100:
        chance = 100
    if chance < 0:
        chance = 0
    return round(chance)


def calc_length(userid, monsterid, number):
    """Calculates the length of a task."""
    user_prayer = users.read_user(userid, key=users.PRAY_KEY)
    combat_level = users.xp_to_level(users.read_user(userid, key=users.COMBAT_XP_KEY))
    equipment = users.read_user(userid, key=users.EQUIPMENT_KEY)
    player_dam, player_acc, player_arm, player_pray = users.get_equipment_stats(equipment)
    monster_arm = mon.get_attr(monsterid, key=mon.ARMOUR_KEY)
    monster_xp = mon.get_attr(monsterid, key=mon.XP_KEY)
    monsters_fought = users.read_user(userid, key=users.MONSTERS_KEY)
    if monsterid in monsters_fought.keys():
        time_bonus = 1 - 0.2 * min(monsters_fought[monsterid] / 5000, 1)
    else:
        time_bonus = 1

    if user_prayer != -1:
        player_dam, player_acc, player_arm = prayer.calc_pray_bonus(userid)

    if mon.get_attr(monsterid, key=mon.DRAGON_KEY) == 1:
        if equipment['7'] == '266' or equipment['7'] == '293':
            monster_base = 1
        else:
            monster_base = 100
    else:
        monster_base = 1
    if monsterid == '87':
        if equipment['5'] == '578':
            monster_base = 1
        else:
            monster_base = 100

    player_potion = equipment['15']
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

    c = combat_level
    dam_multiplier = 1 + player_acc / 200
    base_time = math.floor(number * monster_xp / 10) * time_bonus
    time = round(base_time * monster_arm * monster_base / (player_dam * dam_multiplier + c))

    return base_time, time







def get_task_info(userid):
    """Gets the info associated with a user's slayer task and returns it as a tuple."""
    task = adv.read(userid)
    taskid, userid, finish_time, guildid, channelid, monsterid, monster_name, num_to_kill, chance = task

    time_left = adv.get_delta(finish_time)

    return taskid, userid, time_left, monsterid, monster_name, num_to_kill, chance










def print_chance(userid, monsterid, monster_dam=-1, monster_acc=-1, monster_arm=-1, monster_combat=-1, xp=-1,
                 number=100, dragonfire=False):
    equipment = users.read_user(userid, key=users.EQUIPMENT_KEY)
    player_dam, player_acc, player_arm, player_pray = users.get_equipment_stats(equipment)
    player_combat = users.xp_to_level(users.read_user(userid, key=users.SLAYER_XP_KEY))
    if monster_dam == -1:
        monster_dam = mon.get_attr(monsterid, key=mon.DAMAGE_KEY)
        monster_acc = mon.get_attr(monsterid, key=mon.ACCURACY_KEY)
        monster_arm = mon.get_attr(monsterid, key=mon.ARMOUR_KEY)
        xp = mon.get_attr(monsterid, key=mon.XP_KEY)
        monster_combat = mon.get_attr(monsterid, key=mon.LEVEL_KEY)
    if dragonfire:
        monster_base = 100
    else:
        monster_base = 1

    c = 1 + monster_combat / 200
    d = 1 + player_combat / 99
    dam_multiplier = monster_base + monster_acc / 200
    chance = round(min(100 * max(0, (2 * d * player_arm) / (number / 50 * monster_dam * dam_multiplier + c)), 100))
    # chance = round(min(100 * max(0, (player_arm / (monster_dam * dam_multiplier + 1 + monster_combat / 200)) / 2 + player_combat / 200), 100))

    dam_multiplier = 1 + player_acc / 200
    base_time = math.floor(number * xp / 10)
    time = round(base_time * (monster_arm * monster_base / (player_dam * dam_multiplier + player_combat)))
    out = f'level {monster_combat} monster with {monster_dam} dam {monster_acc} acc {monster_arm} arm giving {xp} xp: ' \
          f'chance: {chance}%, base time: {base_time}, time to kill {number}: {time}, time ratio: {time / base_time}.'
    return out


def print_kill_status(userid, time_left, *args):
    monsterid, monster_name, num_to_kill, length, chance = args[0]
    chance = calc_chance(userid, monsterid, num_to_kill)
    out = f'{SLAYER_HEADER}' \
          f'You are currently killing {mon.add_plural(num_to_kill, monsterid, with_zero=True)} for {length} minutes. ' \
          f'You currently have a {chance}% chance of killing this many monsters without dying. ' \
          f'You can see your loot {time_left}.'
    return out


def print_status(userid, time_left, *args):
    monsterid, monster_name, num_to_kill, chance = args[0]
    chance = calc_chance(userid, monsterid, num_to_kill)
    out = f'{SLAYER_HEADER}' \
          f'You are currently slaying {mon.add_plural(num_to_kill, monsterid, with_zero=True)}. ' \
          f'You can see the results of this slayer task {time_left}. ' \
          f'You currently have a {chance}% chance of succeeding with your current gear. '
    return out


def print_reaper_status(userid, time_left, *args):
    monsterid, monster_name, num_to_kill, chance = args[0]
    chance = calc_chance(userid, monsterid, num_to_kill)
    out = f'{SLAYER_HEADER}' \
          f'You are currently on a reaper task of {mon.add_plural(num_to_kill, monsterid, with_zero=True)}. ' \
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
    out += f'Kill __{mon.add_plural(num_to_kill, monsterid, with_zero=True)}__!\n'
    out += f'This will take {task_length} minutes '
    out += f'and has a success rate of {chance}% with your current gear. '
    return out
