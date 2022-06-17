from miniscape.models import User, Prayer, Item
import string

PRAYER_HEADER = f':pray: __**PRAYER**__ :pray:\n'
PRAYER_POTION = Item.objects.get(name__iexact="prayer potion")
NAME_KEY = None


def calc_pray_bonus(user: User, prayer: Prayer = None):
    if prayer is None:
        prayer = user.prayer_slot

    player_dam, player_acc, player_arm, _ = user.equipment_stats
    player_dam *= 1 + prayer.damage / 50.0
    player_acc *= 1 + prayer.accuracy / 50.0
    player_arm *= 1 + prayer.armour / 50.0
    return player_dam, player_acc, player_arm


def calc_drain_time(user: User):
    # TODO: Port this, not actively in use it appears
    """Calculates the effective drain rate of a prayer."""
    equipped_prayer = user.prayer_slot
    user_potion = user.potion_slot
    user_prayer = user.prayer_level
    prayer_drain = equipped_prayer.drain

    if user_potion == PRAYER_POTION:
        potion_base = 2
    else:
        potion_base = 1

    base_time = float(36 / prayer_drain)
    effective_time = 60 * user_prayer * base_time * potion_base * (1 + prayer_drain / 30)
    return effective_time


def print_info(prayer):
    """Prints information about a particular prayer"""
    prayer: Prayer = Prayer.find_by_name_or_nick(prayer)
    if not prayer:
        return f'{prayer} is not a prayer.'

    out = PRAYER_HEADER
    out += f'**Name**: {prayer.name}\n'
    aliases = prayer.nickname_str_list
    if len(aliases) > 0:
        out += f"**Aliases**: {', '.join(aliases)}\n"
    out += f'**Prayer**: {prayer.level_required}\n'
    out += f'**Drain Rate**: {prayer.drain}\n'
    out += f'\n*{prayer.description}*'
    return out


def print_list(userid, search_term="", allow_empty=True):
    """Lists the prayers the the user can use."""
    if userid:
        user = User.objects.get(id=userid)
        usable_prayers = user.usable_prayers
    else:
        usable_prayers = Prayer.objects.filter(name__icontains=search_term)
    if not usable_prayers and not allow_empty:
        return []
    out = PRAYER_HEADER
    messages = []
    for prayer in usable_prayers:
        out += f'**{string.capwords(prayer.name)}** *(level {prayer.level_required})*\n'
        if len(out) > 1800:
            messages.append(out)
            out = f'{PRAYER_HEADER}'

    out += 'Type `~prayer info [name]` to get more information about a particular prayer.\n'
    messages.append(out)
    return messages


def set_prayer(userid, prayer):
    """Sets a user's prayer."""
    from miniscape import adventures as adv
    user = User.objects.get(id=userid)

    if adv.is_on_adventure(userid):
        return 'You cannot change your prayer while on an adventure.'

    found_prayer = Prayer.find_by_name_or_nick(prayer)
    if not found_prayer:
        return f'{prayer} is not a prayer.'

    if not user.can_use_prayer(found_prayer):
        return f'You cannot use this prayer.'

    user.prayer_slot = found_prayer
    user.save()
    out = f'{PRAYER_HEADER}Your prayer has been set to {string.capwords(found_prayer.name)}!'
    return out
