from django.db import models


class Item(models.Model):

    # TODO:
    # - Verify ItemNickname relationship
    # - Add quest requirement relationship
    # - Add Talisman requirement

    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=200,
                            unique=True)
    plural = models.CharField(max_length=200,
                              blank=True)
    value = models.PositiveIntegerField(default=0)

    # Stats
    damage = models.PositiveIntegerField(default=0)
    accuracy = models.PositiveIntegerField(default=0)
    armour = models.PositiveIntegerField(default=0)
    prayer = models.PositiveIntegerField(default=0)
    slot = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=0)
    xp = models.PositiveIntegerField(default=0)

    # Booleans
    is_gatherable = models.BooleanField(default=False)
    is_tree = models.BooleanField(default=False)
    is_rock = models.BooleanField(default=False)
    is_fish = models.BooleanField(default=False)
    is_pot = models.BooleanField(default=False)
    is_rune = models.BooleanField(default=False)
    is_cookable = models.BooleanField(default=False)
    is_buryable = models.BooleanField(default=False)
    is_max_only = models.BooleanField(default=False)
    is_pet = models.BooleanField(default=False)

    # misc
    pouch = models.PositiveIntegerField(default=0)
    luck_modifier = models.FloatField(default=0)

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

    @classmethod
    def all_pets(cls):
        return Item.objects.all().filter(is_pet=True).order_by('name')

    def __repr__(self):
        return "Item ID %d: %s" % (self.id, self.name)

    def __str__(self):
        return self.__repr__()


class ItemNickname(models.Model):
    class Meta:
        unique_together = (('nickname', 'item'),)

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=200,
                                unique=True)

    def __repr__(self):
        return "Nickname for Item (%s), nickname: %s" % (str(self.item), self.nickname)

    def __str__(self):
        return self.__repr__()
