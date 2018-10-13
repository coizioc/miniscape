from django.db import models


class Monster(models.Model):

    # TODO:
    # - Implement monster nicknames
    # - Implement quest requirements

    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=200,
                            unique=True)
    plural = models.CharField(max_length=200,
                              blank=True,
                              default="s")


    # Stats
    xp = models.PositiveIntegerField(default=0)
    slayer_level_req = models.PositiveIntegerField(default=0)
    damage = models.PositiveIntegerField(default=0)
    accuracy = models.PositiveIntegerField(default=0)
    armour = models.PositiveIntegerField(default=0)

    # Booleans
    is_slayable = models.BooleanField(default=0)
    is_boss = models.BooleanField(default=0)
    is_dragon = models.BooleanField(default=0)

    #  Misc
    min_assignable = models.PositiveIntegerField(default=0)
    max_assignable = models.PositiveIntegerField(default=0)

    MELEE = 0
    RANGE = 0
    MAGIC = 0
    affinity_choices = (
        (MELEE, 'Melee'),
        (RANGE, 'Range'),
        (MAGIC, 'Magic')
    )
    affinity = models.PositiveIntegerField(choices=affinity_choices,
                                           default=MELEE)