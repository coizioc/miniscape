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
    RANGE = 1
    MAGIC = 2
    affinity_choices = (
        (MELEE, 'Melee'),
        (RANGE, 'Range'),
        (MAGIC, 'Magic')
    )
    affinity = models.PositiveIntegerField(choices=affinity_choices,
                                           default=MELEE)

    loot = models.ManyToManyField('Item',
                                  through='MonsterLoot',
                                  through_fields=('monster', 'item'))


class MonsterLoot(models.Model):
    # class Meta:
    #     unique_together = (('item', 'monster', 'rarity', 'min_amount'),)

    item = models.ForeignKey('Item',
                             on_delete=models.CASCADE)

    monster = models.ForeignKey('Monster',
                                on_delete=models.CASCADE)

    min_amount = models.PositiveIntegerField(default=1)
    max_amount = models.PositiveIntegerField(default=1)
    rarity = models.PositiveIntegerField(default=1)

    @property
    def rarity_str(self):
        rarities = {1: 'always',
                    16: 'common',
                    128: 'uncommon',
                    256: 'rare',
                    1024: 'super rare',
                    4096: 'ultra rare',
                    8192: 'super duper rare'}

        try:
            return rarities[self.rarity]
        except KeyError:
            keys = sorted(rarities.keys())
            curr_rarity = ''
            for key in keys:
                if self.rarity > key:
                    curr_rarity = rarities[key]
                else:
                    break

            return curr_rarity
