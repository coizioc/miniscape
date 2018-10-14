from collections import Counter

from django.db import models

from .userinventory import UserInventory
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

        self.skill_level_mapping = {'combat': self.combat_level,
                                    'cb': self.combat_level,
                                    'slayer': self.slayer_level,
                                    'slay': self.slayer_level,
                                    'gather': self.gather_level,
                                    'artisan': self.artisan_level,
                                    'craft': self.artisan_level,
                                    'cook': self.cook_level,
                                    'cooking': self.cook_level,
                                    'pray': self.prayer_level,
                                    'prayer':  self.prayer_level,
                                    'rc': self.rc_level,
                                    'runecrafting': self.rc_level}

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

        self.skill_xp_mapping = {'combat': self.combat_xp,
                                 'cb': self.combat_xp,
                                 'slayer': self.slayer_xp,
                                 'slay': self.slayer_xp,
                                 'gather': self.gather_xp,
                                 'artisan': self.artisan_xp,
                                 'craft': self.artisan_xp,
                                 'cook': self.cook_xp,
                                 'cooking': self.cook_xp,
                                 'pray': self.pray_xp,
                                 'prayer':  self.pray_xp,
                                 'rc': self.rc_xp,
                                 'runecrafting': self.rc_xp}

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
    # - Implement Equipment

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

    # Boosts
    potion_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="item_potion")
    prayer_slot = models.ForeignKey('Prayer', on_delete=models.SET_NULL, null=True)
    active_food = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="item_food")

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

    equipment_slot_strs = ['head_slot',
                           'back_slot',
                           'neck_slot',
                           'ammo_slot',
                           'mainhand_slot',
                           'torso_slot',
                           'offhand_slot',
                           'legs_slot',
                           'hands_slot',
                           'feet_slot',
                           'ring_slot',
                           'pocket_slot',
                           'hatchet_slot',
                           'pickaxe_slot',
                           'potion_slot']

    def get_inventory(self, search=None):
        """ Returns a list of UserInventory Objects related to this user"""
        if search:
            return self._get_name_filtered_inventory(search)
        else:
            return self.userinventory_set.all().order_by('item__name')

    def _get_name_filtered_inventory(self, name):
        """ Returns a list of UserInventory Objects related to user filtered by name"""
        return self.userinventory_set.filter(item__name__icontains=name).order_by('item__name')

    def has_item_by_name(self, item_name):
        if self.get_item_by_name(item_name) is None:
            return False
        else:
            return True

    def get_item_by_item(self, item):
        return self.userinventory_set.filter(item=item)

    def has_item_by_item(self, item):
        item = self.get_item_by_item(item)
        return len(item) > 0

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

    def get_items_by_id(self, item):
        items = self.userinventory_set.filter(item__id=item)
        return items

    def get_items_by_ids(self, items):
        items = self.userinventory_set.filter(item__id__in=items).order_by('item__name')
        return items

    def get_items_by_obj(self, item):
        items = self.userinventory_set.filter(item=item)
        return items

    def get_items_by_objs(self, items):
        items = self.userinventory_set.filter(item__in=items).order_by('item__name')
        return items

    def update_inventory(self, loot, amount=1, remove=False):
        if type(loot) == Item:
            # Need to pass in UserInventory object
            loot = {loot.id: amount}

        loot = Counter(loot)
        for itemid, amount in loot.items():
            item = self.get_items_by_id(itemid)
            if item:
                self._update_inventory_object(item[0], amount=amount, remove=remove)
            else:
                self._add_inventory_item_id(itemid)

    def _update_inventory_item_id(self, loot: str, amount=1,  remove=False):
        item = Item.objects.get(id=loot)
        return self._update_inventory_object(item, amount=amount, remove=remove)

    def _update_inventory_object(self, loot: Item, amount=1, remove=False):
        new_amt = (loot.amount - amount) if remove else (loot.amount + amount)

        if new_amt == 0:
            loot.delete()
        elif new_amt >= 0:
            loot.amount = new_amt
            loot.save()
        else:
            # Negative ??
            raise ValueError("Update would result in negative inventory")

    def _add_inventory_item_id(self, item: str, amount=1):
        obj = Item.objects.get(id=item)
        return self._add_inventory_object(obj, amount=amount)

    def _add_inventory_object(self, loot: Item, amount=1):
        ui = UserInventory(user=self,
                           item=loot,
                           amount=amount)
        ui.save()

    @property
    def max_possible_level(self):
        return 99 * len(self.level_fields)

    @staticmethod
    def _calc_level(xp):
        return xp_to_level(xp)

    @property
    def all_armour(self):
        return {'Head': self.head_slot,
                'Back': self.back_slot,
                'Neck': self.neck_slot,
                'Ammunition': self.ammo_slot,
                'Main-Hand': self.mainhand_slot,
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
        return self.total_level == self.max_possible_level

    @property
    def total_xp(self):
        return sum(self.xp_fields)

    @property
    def plain_name(self):
        return self.name.split("#")[0]

    @property
    def clue_counts(self):
        return [('easy', self.easy_clues),
                ('medium', self.medium_clues),
                ('hard', self.hard_clues),
                ('elite', self.elite_clues),
                ('master', self.master_clues)]

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
