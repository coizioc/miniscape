from miniscape.models import User


def get_display_name(member):
    """Gets the displayed name of a user."""
    if member.nick is None:
        name = member.name
    else:
        name = member.nick
    if User.objects.get(id=member.id).is_ironman:
        name += ' (IM)'
    return name