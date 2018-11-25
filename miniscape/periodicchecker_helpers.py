from miniscape.models import User
from miniscape.models.periodicchecker import PeriodicChecker


def is_next_day():
    """Returns whether the date stored in the PeriodicChecker is the same as the current date or not."""
    return PeriodicChecker.objects.get(id=1).is_next_day()


def reset_dailies():
    """Resets the completion of all dailies."""
    # Clear each user's progress on their dailies.
    for user in User.objects.all():
        user.clear_dailies()

    # Updates the date in the PeriodicChecker to match the current date.
    PeriodicChecker.objects.get(id=1).update_date()
