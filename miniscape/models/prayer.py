from django.db import models


class Prayer(models.Model):

    # TODO:
    # - Verify nickname relationship

    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=200,
                            unique=True)
    description = models.CharField(max_length=1000,
                                   default="Fuck you")
    nick = models.ManyToManyField('PrayerNickname')


    # "Stats"
    level_required = models.PositiveIntegerField(default=0)
    drain = models.PositiveIntegerField(default=0)
    damage = models.PositiveIntegerField(default=0)
    accuracy = models.PositiveIntegerField(default=0)
    armour = models.PositiveIntegerField(default=0)
    chance = models.PositiveIntegerField(default=0)
    luck_factor = models.FloatField(default=0)
    gather = models.FloatField(default=0)

    # Booleans
    keep_factor = models.BooleanField(default=False)

    # Misc
    MELEE = 0
    RANGE = 1
    MAGIC = 2
    affinity_choices = (
        (MELEE, 'Melee'),
        (RANGE, 'Range'),
        (MAGIC, 'Magic')
    )
    affinity = models.PositiveIntegerField(choices=affinity_choices,
                                           default=None,
                                           null=True)

    # Relationships
    quest_req = models.ForeignKey('Quest',
                                  on_delete=models.SET_NULL,
                                  null=True)

    def __repr__(self):
        return "Prayer \"%s\" (id: %d)" % (self.name, self.id)

    def __str__(self):
        return self.__repr__()


class PrayerNickname(models.Model):
    class Meta:
        unique_together = (('nickname', 'real_prayer'),)

    real_prayer = models.ForeignKey(Prayer, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=200,
                                unique=True)

    def __repr__(self):
        return "Nickname for Prayer (%s), nickname: %s" % (str(self.real_prayer), self.nickname)

    def __str__(self):
        return self.__repr__()
