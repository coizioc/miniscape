from django.db import models


class Item(models.Model):

    # TODO:
    # - Verify ItemNickname relationship
    # - Add quest requirement relationship
    # - Add Talisman requirement

    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=200,
                            unique=True)
    nick = models.ManyToManyField('ItemNickname')
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
    food_value = models.PositiveIntegerField(default=0)


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

    clue_loot = models.ManyToManyField('Item',
                                       through='ClueLoot',
                                       through_fields=('clue_item', 'loot_item'))

    @classmethod
    def all_pets(cls):
        return Item.objects.filter(is_pet=True).order_by('name')

    @classmethod
    def find_by_name_or_nick(cls, name):
        item = Item.objects.filter(name=name)
        if item:
            return item[0]
        else:
            nick = ItemNickname.objects.filter(nickname=name)
            if nick:
                return nick[0].real_item
            else:
                return None

    @classmethod
    def all_food(cls):
        return Item.objects.filter(food_value__gte=1).order_by('name')

    @classmethod
    def find_food_by_name(cls, name):
        return Item.objects.filter(name__icontains=name, food_value__gte=1).order_by('name')

    @property
    def is_food(self):
        return self.food_value > 0

    @property
    def is_equippable(self):
        return self.slot > 0

    def __repr__(self):
        return "Item ID %d: %s" % (self.id, self.name)

    def __str__(self):
        return self.__repr__()


class ItemNickname(models.Model):
    class Meta:
        unique_together = (('nickname', 'real_item'),)

    real_item = models.ForeignKey(Item, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=200,
                                unique=True)

    def __repr__(self):
        return "Nickname for Item (%s), nickname: %s" % (str(self.real_item), self.nickname)

    def __str__(self):
        return self.__repr__()
