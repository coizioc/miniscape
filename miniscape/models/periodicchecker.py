import datetime
from django.db import models


class PeriodicChecker(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    last_check_datetime = models.DateTimeField('last_check', auto_now_add=True)

    def is_next_day(self):
        """Checks if the current date differs from that of the PeriodicChecker."""
        return True if self.last_check_datetime.date() < datetime.datetime.now().date() else False

    def update_date(self):
        """Updates the date stored in the PeriodicChecker"""
        self.last_check_datetime = datetime.datetime.now()
        self.save()

    def __repr__(self):
        return f"Last check: {self.last_check_datetime}"

    def __str__(self):
        return self.__repr__()
