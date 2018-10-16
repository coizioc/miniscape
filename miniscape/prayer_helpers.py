from miniscape.models import User, Prayer

PRAYER_HEADER = f':pray: __**PRAYER**__ :pray:\n'
NAME_KEY = None


def calc_pray_bonus(user: User, prayer: Prayer =None):
    if prayer is None:
        prayer = user.prayer_slot

    player_dam, player_acc, player_arm, player_pray = user.equipment_stats
    player_dam *= 1 + prayer.damage / 50.0
    player_acc *= 1 + prayer.accuracy / 50.0
    player_arm *= 1 + prayer.armour / 50.0
    return player_dam, player_acc, player_arm


def calc_drain_time(userid, prayerid):
    # TODO: Port this, not actively in use it appears
    """Calculates the effective drain rate of a prayer."""
    equipment_prayer = user.prayer_slot
    user_equipment = users.read_user(userid, key=users.EQUIPMENT_KEY)
    equipment_prayer = users.get_equipment_stats(user_equipment)[3]
    user_potion = user_equipment['15']
    user_prayer = users.get_level(userid, key=users.PRAY_XP_KEY)
    prayer_drain = get_attr(prayerid, key=DRAIN_KEY)

    if user_potion == '199':
        potion_base = 2
    else:
        potion_base = 1

    base_time = float(36 / prayer_drain)
    effective_time = 60 * user_prayer * base_time * potion_base * (1 + equipment_prayer / 30)
    return effective_time


def print_info(prayer):
    """Prints information about a particular prayer"""
    prayer: Prayer = Prayer.find_by_name_or_nick(prayer)
    if not prayer:
        return f'{prayer} is not a prayer.'

    out = PRAYER_HEADER
    out += f'**Name**: {prayer.name}\n'
    aliases = prayer.nickname_str_list
    if aliases > 0:
        out += f"**Aliases**: {', '.join(aliases)}\n"
    out += f'**Prayer**: {prayer.level_required}\n'
    out += f'**Drain Rate**: {prayer.drain}\n'
    out += f'\n*{prayer.description}*'
    return out


def print_list(userid):
    """Lists the prayers the the user can use."""
    user = User.objects.get(id=userid)
    usable_prayers = user.usable_prayers

    out = PRAYER_HEADER
    messages = []
    for prayer in usable_prayers:
        out += f'**{prayer.name.title()}** *(level {prayer.level_required})*\n'
        if len(out) > 1800:
            messages.append(out)
            out = f'{PRAYER_HEADER}'

    out += 'Type `~prayer info [name]` to get more information about a particular prayer.'
    messages.append(out)
    return messages


def set_prayer(userid, prayer):
    """Sets a user's prayer."""
    from miniscape import adventures as adv
    user = User.objects.get(id=userid)

    if adv.is_on_adventure(userid):
        return 'You cannot change your prayer while on an adventure.'

    prayer = Prayer.find_by_name_or_nick(prayer)
    if not prayer:
        return f'{prayer} is not a prayer.'

    if not user.can_use_prayer(prayer):
        return f'You cannot use this prayer.'

    user.prayer_slot = prayer
    user.save()
    out = f'{PRAYER_HEADER}Your prayer has been set to {prayer.name.title()}!'
    return out
