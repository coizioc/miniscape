from django.db import models


class Prayer(models.Model):

    # TODO:
    # - Verify nickname relationship

    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=200,
                            unique=True)
    description = models.CharField(max_length=1000,
                                   default="Fuck you")

    # "Stats"
    level_required = models.PositiveIntegerField(default=0)
    drain = models.PositiveIntegerField(default=0)
    damage = models.PositiveIntegerField(default=0)
    accuracy = models.PositiveIntegerField(default=0)
    armour = models.PositiveIntegerField(default=0)
    chance = models.PositiveIntegerField(default=0)
    factor = models.PositiveIntegerField(default=0)
    gather = models.PositiveIntegerField(default=0)

    # Booleans
    keep_factor = models.BooleanField(default=False)

    # Relationships
    quest_req = models.ForeignKey('Quest',
                                  on_delete=models.SET_NULL,
                                  null=True)


class PrayerNickname(models.Model):

    prayer = models.ForeignKey(Prayer, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=200,
                                unique=True)
