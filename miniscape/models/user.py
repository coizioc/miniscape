from collections import Counter

from django.db import models

from .quest import Quest
from .prayer import Prayer
from .monster import Monster
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
                          self.prayer_xp,
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
                                 'pray': self.prayer_xp,
                                 'prayer':  self.prayer_xp,
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

        self.equipment_slot_strs = equipment_slot_strs = ['head_slot',
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
    prayer_xp = models.BigIntegerField(default=0)
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
    is_mod = models.BooleanField(default=False)
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

    completed_quests = models.ManyToManyField('Quest',
                                              through='UserQuest',
                                              through_fields=('user', 'quest'))

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

    def has_item_amount_by_item(self, item: Item, amount):
        item = self.get_item_by_item(item)
        if not item:
            return False
        elif item[0].amount >= amount:
            return True
        else:
            return False

    def has_item_amount_by_counter(self, loot: Counter({Item: int})):
        for item, amt in loot.items():
            if not self.has_item_amount_by_item(item, amt):
                return False
        else:
            return True

    def get_item_by_name(self, item_name):
        """ Get a particular item from user """
        item = Item.objects.filter(name=item_name)
        if item:
            return self.userinventory_set.filter(item=item[0])

        item = ItemNickname.objects.filter(nickname=item_name)
        if item:
            return self.userinventory_set.filter(item=item[0])

        return None

    def get_item_count(self, item=None, itemid=None, itemname=None):
        """ Returns the number of items in user inventory by either object, name, or ID"""
        if item:
            ui = self.get_items_by_obj(item)[0]
        elif itemid:
            ui = self.get_item_by_id(itemid)
        elif itemname:
            ui = self.get_item_by_name(itemname)

        if ui:
            return ui.amount
        return 0

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
        items = self.userinventory_set.get_or_create(item=item)
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
            if type(itemid) == Item:
                item = self.get_items_by_obj(itemid)
                itemid = item[0].item.id
            else:
                item = self.get_items_by_id(itemid)

            if item:
                self._update_inventory_object(item[0], amount=amount, remove=remove)
            else:
                item = Item.objects.get(id=itemid)
                self._add_inventory_object(item, amount=amount)
        self.save()

    def _update_inventory_item_id(self, loot: str, amount=1,  remove=False):
        item = Item.objects.get(id=loot)
        return self._update_inventory_object(item, amount=amount, remove=remove)

    def _update_inventory_object(self, loot: UserInventory, amount=1, remove=False):
        new_amt = (loot.amount - amount) if remove else (loot.amount + amount)

        if new_amt == 0:
            loot.delete()
        elif new_amt >= 0:
            loot.amount = new_amt
            loot.save()
        else:
            # Negative ??
            raise ValueError("Update would result in negative inventory")

    def _add_inventory_item_id(self, item: Item, amount=1):
        obj = Item.objects.get(id=int(item))
        return self._add_inventory_object(obj, amount=amount)

    def _add_inventory_object(self, loot: Item, amount=1):
        ui = UserInventory(user=self,
                           item=loot,
                           amount=amount)
        ui.save()

    def lock_item(self, itemname):
        item: UserInventory = self.get_item_by_name(itemname)
        if not item:
            return False
        else:
            item = item[0]
            item.is_locked = True
            item.save()
            return True

    def unlock_item(self, itemname):
        item: UserInventory = self.get_item_by_name(itemname)
        if not item:
            return False
        else:
            item = item[0]
            item.is_locked = False
            item.save()
            return True

    def monster_kills(self, search=None):
        if search:
            return self.playermonsterkills_set.\
                filter(monster__name__icontains=search)\
                .order_by('monster__name')
        else:
            return self.playermonsterkills_set.all().order_by('monster__name')

    def add_kills(self, monster: Monster, num: int):
        mk: PlayerMonsterKills = self.playermonsterkills_set.get_or_create(user=self,
                                                                           monster=monster)[0]
        mk.amount += num
        mk.save()

    def can_use_prayer(self, prayer: Prayer):
        # Validate prayer level
        if self.prayer_level >= prayer.level_required:
            # Validate quest req
            if not prayer.quest_req or prayer.quest_req in self.completed_quests_list:
                return True

        # Default
        return False

    def drink(self, potion):
        if type(potion) == Item:
            pot = potion
            if pot.is_pot:
                self.potion_slot = pot
            else:
                return False
        else:
            pot = Item.find_by_name_or_nick(potion)
            if pot and pot.is_pot:
                self.potion_slot = pot
            else:
                return False

        self.update_inventory(Counter({pot: 1}), remove=True)
        self.save()
        return True

    def reset_account(self):
        """ Completely resets a user's account. Primarily used by ~ironman"""
        self.clear_armour()
        self.clear_inventory()
        self.clear_stats()
        self.clear_quests()
        self.clear_monster_kills()
        self.clear_boosts()
        self.clear_clues()
        self.clear_dailies()
        self.clear_flags()
        self.save()

    def clear_inventory(self):
        """ Deletes _all_ items in user's inventory, incl coins"""
        ui = UserInventory.objects.filter(user=self)
        ui.delete()

    def clear_stats(self):
        """ Reset's user's stats to 0 xp"""
        for stat in self.xp_fields_str:
            setattr(self, stat, 0)
        self.save()

    def clear_armour(self):
        """ Clear users armour, prayer, potion"""
        for eq in self.equipment_slot_strs:
            setattr(self, eq, None)
        self.save()

    def clear_quests(self):
        self.userquest_set.all().delete()
        pass

    def clear_monster_kills(self):
        mk = PlayerMonsterKills.objects.filter(user=self)
        mk.delete()

    def clear_boosts(self):
        self.potion_slot = None
        self.prayer_slot = None
        self.active_food = None
        self.save()

    def clear_clues(self):
        self.easy_clues = 0
        self.medium_clues = 0
        self.hard_clues = 0
        self.elite_clues = 0
        self.master_clues = 0
        self.save()

    def clear_dailies(self):
        self.is_reaper_complete = False
        self.is_vis_complete = False
        self.vis_attempts = 0
        self.save()

    def clear_flags(self):
        self.is_ironman = False
        self.save()

    def has_quest_req_for_quest(self, quest: Quest, cached=None):
        complete = cached if cached else self.completed_quests_list
        for quest in quest.quest_reqs.all():
            if quest not in complete:
                return False
        return True

    def has_completed_quest(self, quest):
        return quest in self.completed_quests_list

    def has_items_for_quest(self, quest: Quest):
        quest_items = quest.required_items
        if quest_items:
            quest_items = {qir.item : qir.amount for qir in quest_items}
            quest_items = Counter(quest_items)
            return self.has_item_amount_by_counter(quest_items)
        else:
            return True

    @property
    def usable_prayers(self):
        prayers = Prayer.objects.filter(level_required__lte=self.prayer_level)
        ret = []
        for p in prayers:
            if p.quest_req and p.quest_req in self.completed_quests_list:
                ret.append(p)
            elif not p.quest_req:
                ret.append(p)

        return ret

    @property
    def completed_quests_list(self):
        return [uq.quest for uq in self.userquest_set.all()]

    @property
    def num_quests_complete(self):
        return len(self.completed_quests_list)

    @property
    def is_eating(self):
        return self.active_food is not None

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
        return self._calc_level(self.prayer_xp)

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

    @property
    def luck_factor(self) -> float:
        prayer_luck = self.prayer_slot.luck_factor if self.prayer_slot else 0
        ring_luck = self.ring_slot.luck_modifier if self.ring_slot else 0
        return max(1, prayer_luck, ring_luck)

    def __repr__(self):
        return "User ID %d: %s" % (self.id, self.name)

    def __str__(self):
        return self.__repr__()
