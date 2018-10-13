from collections import Counter

from django.db import models
from .item import Item, ItemNickname
from django.core.exceptions import ObjectDoesNotExist
from .playermonsterkills import PlayerMonsterKills
from cogs.helper.users import xp_to_level


class User(models.Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level_fields = [self.combat_level,
                             self.slayer_level,
                             self.gather_level,
                             self.artisan_level,
                             self.cook_level,
                             self.prayer_level,
                             self.rc_level
                             ]

        self.xp_fields = [self.combat_xp,
                          self.slayer_xp]

    # TODO:
    # - test inventory (including locked items)
    # - Implement Monsters killed
    # - Implement Equipment
    # - Implement Food
    # - Implement current prayer
    # - Implement completed quests

    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=200,
                            blank=True,
                            default="")
    nick = models.CharField(max_length=200,
                            blank=True,
                            default="",
                            null=True)

    # Stats
    combat_xp = models.BigIntegerField(default=0)
    slayer_xp = models.BigIntegerField(default=0)
    gather_xp = models.BigIntegerField(default=0)
    artisan_xp = models.BigIntegerField(default=0)
    cook_xp = models.BigIntegerField(default=0)
    pray_xp = models.BigIntegerField(default=0)
    rc_xp = models.BigIntegerField(default=0)


    # Clues
    easy_clues = models.PositiveIntegerField(default=0)
    medium_clues = models.PositiveIntegerField(default=0)
    hard_clues = models.PositiveIntegerField(default=0)
    elite_clues = models.PositiveIntegerField(default=0)
    master_clues = models.PositiveIntegerField(default=0)

    # Flags
    is_ironman = models.BooleanField(default=False)
    is_reaper_complete = models.BooleanField(default=False)
    is_vis_complete = models.BooleanField(default=False)

    # Misc
    vis_attempts = models.PositiveIntegerField(default=0)

    items = models.ManyToManyField('Item',
                                   through='UserInventory',
                                   through_fields=('user', 'item'))

    monsters = models.ManyToManyField('Monster',
                                      through=PlayerMonsterKills,
                                      through_fields=('user', 'monster'))

    def get_inventory(self):
        """ Returns a list of UserInventory Objects related to this user"""
        return self.userinventory_set.all().order_by('item__name')

    def get_name_filtered_inventory(self, name):
        """ Returns a list of UserInventory Objects related to user filtered by name"""
        return self.userinventory_set.filter(item__name__icontains=name).order_by('item__name')

    def get_item(self, item_id=None, item_name=None):
        """ Get a particular item from user """
        if item_id is None and item_name is None:
            raise ValueError("Both item_id and item_name in user.get_item can't be None, dipshit")
        elif item_id is not None:
            return self.userinventory_set.get(item=Item.objects.get(id=item_id))
        elif item_name is not None:
            try:
                return self.userinventory_set.get(item=Item.objects.get(item_name))
            except ObjectDoesNotExist:
                    item = ItemNickname(nickname=item_name).item
                    return self.userinventory_sert.get(item=item)

    def get_pets(self):
        """ Returns all pets owned by a user """
        return self.userinventory_set.filter(item__is_pet=True).order_by('item__name')

    def get_items_by_id(self, items):
        items = self.userinventory_set.filter(item__id__in=items).order_by('item__name')
        return items

    def update_inventory(self, loot, remove=False):
        loot = Counter(loot)
        items = self.get_items_by_id(loot.keys())
        for item in items:
            print(item.amount)
            if remove:
                item.amount -= loot[str(item.item.id)]
            else:
                item.amount += loot[str(item.item.id)]
            item.save()

    @staticmethod
    def _calc_level(xp):
        return xp_to_level(xp)

    @property
    def combat_level(self):
        return self._calc_level(self.combat_xp)

    @property
    def slayer_level(self):
        return self._calc_level(self.slayer_xp)

    @property
    def gather_level(self):
        return self._calc_level(self.gather_xp)

    @property
    def artisan_level(self):
        return self._calc_level(self.artisan_xp)

    @property
    def cook_level(self):
        return self._calc_level(self.cook_xp)

    @property
    def prayer_level(self):
        return self._calc_level(self.pray_xp)

    @property
    def rc_level(self):
        return self._calc_level(self.rc_xp)

    @property
    def total_level(self):
        return sum(self.level_fields)

    @property
    def is_maxed(self):
        return self.total_level == (99 * len(self.level_fields))

    @property
    def plain_name(self):
        return self.name.split("#")[0]

    def __repr__(self):
        return "User ID %d: %s" % (self.id, self.name)

    def __str__(self):
        return self.__repr__()
