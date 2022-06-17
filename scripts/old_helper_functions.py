# These are old functions that are no longer in use and were around for debugging etc

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
