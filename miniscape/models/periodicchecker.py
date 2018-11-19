from django.db import models


class PeriodicChecker(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    last_check_datetime = models.DateTimeField('Last Check')

    def __repr__(self):
        return f"Last check occurred at {self.last_check_datetime}"

    def __str__(self):
        return self.__repr__()