from miniscape.models import User, Prayer


def calc_pray_bonus(user: User, prayer: Prayer =None):
    if prayer is None:
        prayer = user.prayer_slot

    player_dam, player_acc, player_arm, player_pray = user.equipment_stats
    player_dam *= 1 + prayer.damage / 50.0
    player_acc *= 1 + prayer.accuracy / 50.0
    player_arm *= 1 + prayer.armour / 50.0
    return player_dam, player_acc, player_arm
