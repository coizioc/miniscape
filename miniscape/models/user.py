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

        self.level_fields_str = ['combat_level',
                                 'slayer_level',
                                 'gather_level',
                                 'artisan_level',
                                 'cook_level',
                                 'prayer_level',
                                 'rc_level']

        self.xp_fields = [self.combat_xp,
                          self.slayer_xp,
                          self.gather_xp,
                          self.artisan_xp,
                          self.cook_xp,
                          self.pray_xp,
                          self.rc_xp]

        self.xp_fields_str = ['combat_xp',
                              'slayer_xp',
                              'gather_xp',
                              'artisan_xp',
                              'cook_xp',
                              'pray_xp',
                              'rc_xp']

        self.equipment_slots = [self.head_slot,
                                self.back_slot,
                                self.neck_slot,
                                self.ammo_slot,
                                self.mainhand_slot,
                                self.torso_slot,
                                self.offhand_slot,
                                self.legs_slot,
                                self.hands_slot,
                                self.feet_slot,
                                self.ring_slot,
                                self.pocket_slot,
                                self.hatchet_slot,
                                self.pickaxe_slot,
                                self.potion_slot]

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

    # Armour
    head_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="item_head")
    back_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="item_back")
    neck_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="item_neck")
    ammo_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="item_ammo")
    mainhand_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="item_mainhand")
    torso_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="item_torso")
    offhand_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="item_offhand")
    legs_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="item_legs")
    hands_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="item_hands")
    feet_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="item_feet")
    ring_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="item_ring")
    pocket_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="item_pocket")
    hatchet_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="item_hatchet")
    pickaxe_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="item_pickaxe")
    potion_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="item_potion")
    # Prayer
    prayer_slot = models.ForeignKey('Prayer', on_delete=models.SET_NULL, null=True)

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

    completed_quests = models.ManyToManyField('Quest')


    def get_inventory(self):
        """ Returns a list of UserInventory Objects related to this user"""
        return self.userinventory_set.all().order_by('item__name')

    def get_name_filtered_inventory(self, name):
        """ Returns a list of UserInventory Objects related to user filtered by name"""
        return self.userinventory_set.filter(item__name__icontains=name).order_by('item__name')

    def has_item_by_name(self, item_name):
        if self.get_item_by_name(item_name) is None:
            return False
        else:
            return True

    def has_item_amount_by_name(self, item_name, amount):
        item = self.get_item_by_name(item_name)
        if not item:
            return False
        elif item[0].amount >= amount:
            return True
        else:
            return False

    def get_item_by_name(self, item_name):
        """ Get a particular item from user """
        item = Item.objects.filter(name=item_name)
        if item:
            return self.userinventory_set.filter(item=item[0])

        item = ItemNickname.objects.filter(nickname=item_name)
        if item:
            return self.userinventory_set.filter(item=item[0])

        return None

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
    def all_armour(self):
        return {'Head': self.head_slot,
                'Back': self.back_slot,
                'Neck': self.neck_slot,
                'Ammunition': self.ammo_slot,
                'Main-Hand': self.ammo_slot,
                'Torso': self.torso_slot,
                'Off-Hand': self.offhand_slot,
                'Legs': self.legs_slot,
                'Hands': self.hands_slot,
                'Feet': self.feet_slot,
                'Ring': self.ring_slot,
                'Pocket': self.pocket_slot,
                'Hatchet': self.hatchet_slot,
                'Pickaxe': self.pickaxe_slot,
                'Potion': self.potion_slot
                }

    @property
    def damage(self):
        damage = 0
        for item in self.equipment_slots:
            if item:
                damage += item.damage
        return damage

    @property
    def accuracy(self):
        accuracy = 0
        for item in self.equipment_slots:
            if item:
                accuracy += item.accuracy
        return accuracy

    @property
    def armour(self):
        armour = 0
        for item in self.equipment_slots:
            if item:
                armour += item.armour
        return armour

    @property
    def prayer_bonus(self):
        prayer_bonus = 0
        for item in self.equipment_slots:
            if item:
                prayer_bonus += item.prayer
        return prayer_bonus

    @property
    def equipment_stats(self):
        return self.damage, self.accuracy, self.armour, self.prayer_bonus

    @property
    def quests_completed(self):
        return len(self.qu)

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
    def total_xp(self):
        return sum(self.xp_fields)

    @property
    def plain_name(self):
        return self.name.split("#")[0]

    def monster_kills(self, search=None):
        if search:
            return self.playermonsterkills_set.\
                filter(monster__name__icontains=search)\
                .order_by('monster__name')
        else:
            return self.playermonsterkills_set.all().order_by('monster__name')

    def __repr__(self):
        return "User ID %d: %s" % (self.id, self.name)

    def __str__(self):
        return self.__repr__()
