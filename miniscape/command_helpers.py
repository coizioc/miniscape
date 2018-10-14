from miniscape.models import Item, User, UserInventory


def print_inventory(person, search):
    """Prints a list of a user's inventory into discord message-sized chunks."""
    name = person.nick if person.nick else person.plain_name

    if search:
        inventory = person.get_name_filtered_inventory(search)
    else:
        inventory = person.get_inventory()

    lock_template = "**%s (:lock:)**: %s. *(value: %s, %s ea)*\n"
    unlock_template = "**%s**: %s. *(value: %s, %s ea)*\n"

    messages = [(lock_template if item.is_locked else unlock_template)
                % (
                    item.item.name.title(),
                    '{:,}'.format(item.amount),
                    '{:,}'.format(item.total_value),
                    '{:,}'.format(item.item.value)
                ) for item in inventory]

    ret = []
    header = f":moneybag: __**{name.upper()}'S INVENTORY**__ :moneybag:\n"
    out = header
    for message in messages:
        if len(out) + len(message) > 1800:
            ret.append(out)
            out = header
        out = out + message

    # Make sure we append our final message to ret
    ret.append(out)
    return ret


def print_pets(person):
    """Prints a formatted list of pets a user has."""

    user_pets = [item.item for item in person.get_pets()]
    all_pets = Item.all_pets()

    pets_header = f':cat: __**PETS**__ :dog:\n'
    messages = []
    out = pets_header
    for pet in all_pets:
        if pet in user_pets:
            out +=  f"**{pet.name.title()}**\n"
        else:
            out += f'{pet.name.title()}\n'

        if len(out) > 1900:
            messages.append(out)
            out = pets_header

    out += f'{len(user_pets)}/{len(all_pets)}'
    messages.append(out)
    return messages


def eat(author, item):
    if item == 'none' or item == 'nothing':
        author.active_food = None
        author.save()
        return f'You are now eating nothing.'

    item = Item.find_food_by_name(item)[0]
    all_food = Item.all_food()
    if item in Item.all_food():
        author.active_food = item
        author.save()
        # TODO: Readd the pluaralization here per this comment
        # return f'You are now eating {items.add_plural(0, itemid)}!'
        return f'You are now eating {item.name}'
    else:
        return f'You cannot eat {item.name}.'



