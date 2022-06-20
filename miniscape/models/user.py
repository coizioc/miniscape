import logging
import string
from collections import Counter
from typing import Tuple, List, Dict

from django.db import models

import config
from .quest import Quest
from .prayer import Prayer
from .monster import Monster
from .userinventory import UserInventory
from .item import Item, ItemNickname
from .playermonsterkills import PlayerMonsterKills

XP_TO_LEVEL_MAP = {'0': 1,
                   '81': 2,
                   '174': 3,
                   '276': 4,
                   '388': 5,
                   '512': 6,
                   '650': 7,
                   '801': 8,
                   '969': 9,
                   '1154': 10,
                   '1358': 11,
                   '1583': 12,
                   '1832': 13,
                   '2107': 14,
                   '2411': 15,
                   '2746': 16,
                   '3115': 17,
                   '3523': 18,
                   '3973': 19,
                   '4470': 20,
                   '5018': 21,
                   '5624': 22,
                   '6291': 23,
                   '7028': 24,
                   '7842': 25,
                   '8740': 26,
                   '9730': 27,
                   '10824': 28,
                   '12031': 29,
                   '13363': 30,
                   '14833': 31,
                   '16456': 32,
                   '18247': 33,
                   '20224': 34,
                   '22406': 35,
                   '24815': 36,
                   '27473': 37,
                   '30408': 38,
                   '33648': 39,
                   '37224': 40,
                   '41171': 41,
                   '45529': 42,
                   '50339': 43,
                   '55649': 44,
                   '61512': 45,
                   '67983': 46,
                   '75127': 47,
                   '83014': 48,
                   '91721': 49,
                   '101333': 50,
                   '111945': 51,
                   '123660': 52,
                   '136593': 53,
                   '150872': 54,
                   '166636': 55,
                   '184039': 56,
                   '203253': 57,
                   '224466': 58,
                   '247885': 59,
                   '273741': 60,
                   '302287': 61,
                   '333803': 62,
                   '368599': 63,
                   '407014': 64,
                   '449427': 65,
                   '496253': 66,
                   '547952': 67,
                   '605031': 68,
                   '668050': 69,
                   '737627': 70,
                   '814444': 71,
                   '899256': 72,
                   '992894': 73,
                   '1096277': 74,
                   '1210420': 75,
                   '1336442': 76,
                   '1475580': 77,
                   '1629199': 78,
                   '1798807': 79,
                   '1986067': 80,
                   '2192817': 81,
                   '2421086': 82,
                   '2673113': 83,
                   '2951372': 84,
                   '3258593': 85,
                   '3597791': 86,
                   '3972293': 87,
                   '4385775': 88,
                   '4842294': 89,
                   '5346331': 90,
                   '5902830': 91,
                   '6517252': 92,
                   '7195628': 93,
                   '7944613': 94,
                   '8771557': 95,
                   '9684576': 96,
                   '10692628': 97,
                   '11805605': 98,
                   '13034430': 99}


def xp_to_level(xp):
    """Converts a  user's xp into its equivalent level based on an XP table."""
    xp = int(xp)
    for level_xp in XP_TO_LEVEL_MAP:
        if int(level_xp) > xp:
            return int(XP_TO_LEVEL_MAP[level_xp]) - 1
    else:
        return 99



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
                                    'prayer': self.prayer_level,
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
                                 'prayer': self.prayer_xp,
                                 'rc': self.rc_xp,
                                 'runecrafting': self.rc_xp}

        self.xp_fields_str = ['combat_xp',
                              'slayer_xp',
                              'gather_xp',
                              'artisan_xp',
                              'cook_xp',
                              'prayer_xp',
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

    def get_food(self):
        """ Returns a list of UserInventory Objects related to this user"""
        return self.userinventory_set.filter(item__food_value__gte="1").order_by('item__name')

    def has_item_by_name(self, item_name):
        if not self.get_item_by_name(item_name):
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

    def has_item_amount_by_counter(self, loot: Counter({Item: int})) -> bool:
        for item, amt in loot.items():
            if not self.has_item_amount_by_item(item, amt):
                return False
        else:
            return True

    def get_item_by_name(self, item_name):
        """ Get a particular item from user """
        item = Item.objects.filter(name=item_name)
        if item:
            ret = self.userinventory_set.filter(item=item[0])
            return ret

        item = ItemNickname.objects.filter(nickname=item_name)
        if item:
            ret = self.userinventory_set.filter(item=item[0])
            return ret

        return None

    def get_item_count(self, item=None, itemid=None, itemname=None) -> int:
        """ Returns the number of items in user inventory by either object, name, or ID"""
        if item:
            ui = self.get_items_by_obj(item)
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

    def get_items_by_obj(self, item) -> Item:
        item, created = self.userinventory_set.get_or_create(item=item)
        if created:
            item.amount = 0

        return item

    def get_items_by_objs(self, items):
        items = self.userinventory_set.filter(item__in=items).order_by('item__name')
        return items

    def update_inventory(self, loot, amount=1, remove=False):
        if type(loot) == Item:
            logging.getLogger(__name__).info("got loot requst where loot is Item type. This is deprecated. Pls fix")
            # Need to pass in UserInventory object
            loot = {loot.id: amount}

        loot = Counter(loot)
        for i, amount in loot.items():
            if type(i) == Item:
                item = self.get_items_by_obj(i)
            else:
                # This exception shouldn't happen, don't send bad data to here
                try:
                    item = self.get_items_by_id(i)[0]
                except IndexError:
                    item = None

            if item:
                self._update_inventory_object(item, amount=amount, remove=remove)
            else:
                # This should never happen
                item = Item.objects.get(id=i)
                self._add_inventory_object(item, amount=amount)
        self.save()

    def _update_inventory_item_id(self, loot: str, amount=1, remove=False):
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

    def lock_item(self, item_name):
        item: UserInventory = self.get_item_by_name(item_name)
        if not item:
            return False
        else:
            item = item[0]
            item.is_locked = True
            item.save()
            return True

    def unlock_item(self, item_name) -> bool:
        item: UserInventory = self.get_item_by_name(item_name)
        if not item:
            return False
        else:
            item = item[0]
            item.is_locked = False
            item.save()
            return True

    def monster_kills(self, search=None):  # Returns a queryset of MonsterKill objects but idk how to represent that
        if search:
            return self.playermonsterkills_set. \
                filter(monster__name__icontains=search) \
                .order_by('monster__name')
        else:
            return self.playermonsterkills_set.all().order_by('monster__name')

    def add_kills(self, monster: Monster, num: int):
        mk, created = self.playermonsterkills_set.get_or_create(user=self,
                                                                monster=monster)

        if created:
            mk.amount = 0

        mk.amount += num
        mk.save()

    def can_use_prayer(self, prayer: Prayer) -> bool:
        # Validate prayer level
        if self.prayer_level >= prayer.level_required:
            # Validate quest req
            if not prayer.quest_req or prayer.quest_req in self.completed_quests_list:
                return True

        # Default
        return False

    def drink(self, potion) -> bool:
        found_item = Item.find_by_name_or_nick(potion)
        if not self.has_item_by_item(found_item):
            return False
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

    def has_quest_req_for_quest(self, quest: Quest, cached=None) -> bool:
        complete = cached if cached else self.completed_quests_list
        for quest in quest.quest_reqs.all():
            if quest not in complete:
                return False
        return True

    def has_completed_quest(self, quest) -> bool:
        return quest in self.completed_quests_list

    def has_items_for_quest(self, quest: Quest) -> bool:
        quest_items = quest.required_items
        if quest_items:
            quest_items = {qir.item: qir.amount for qir in quest_items}
            quest_items = Counter(quest_items)
            return self.has_item_amount_by_counter(quest_items)
        else:
            return True

    def print_account(self, print_equipment=True) -> str:
        name_to_use = self.nick if self.nick else self.name
        out = f'{config.COMBAT_EMOJI} __**{name_to_use}**__ {config.COMBAT_EMOJI}\n'

        # TODO: This can probably be done better
        skill_names = ["combat", "slayer", "gather", "artisan", "cook", "prayer", "runecrafting"]
        for skill, level, skill_name in zip(self.xp_fields_str, self.level_fields_str, skill_names):
            xp_formatted = '{:,}'.format(getattr(self, skill, 0))
            out += f'**{string.capwords(skill_name)} Level**: {getattr(self, level, 0)} *({xp_formatted} xp)*\n'

        out += f'**Skill Total**: {self.total_level}/{self.max_possible_level}\n\n'
        out += f'**Quests Completed**: {len(self.completed_quests_list)}/{len(Quest.objects.all())}\n\n'
        if print_equipment:
            out += self.print_equipment()
        return out

    def print_equipment(self, with_header=False) -> str:
        armour_print_order = ['Head', 'Back', 'Neck', 'Ammunition', 'Main-Hand', 'Torso', 'Off-Hand',
                              'Legs', 'Hands', 'Feet', 'Ring', 'Pocket', 'Hatchet', 'Pickaxe', 'Potion']

        if with_header:
            name_to_use = self.nick if self.nick else self.name
            out = f'{config.COMBAT_EMOJI} __**{name_to_use}**__ {config.COMBAT_EMOJI}\n'
        else:
            out = ''

        damage, accuracy, armour, prayer = self.equipment_stats
        out += f'**Damage**: {damage}\n' \
               f'**Accuracy**: {accuracy}\n' \
               f'**Armour**: {armour}\n' \
               f'**Prayer Bonus**: {prayer}\n'

        if self.prayer_slot:
            out += f'**Active Prayer**: {self.prayer_slot.name}\n'
        else:
            out += f'**Active Prayer**: none\n'

        if self.active_food:
            out += f'**Active Food**: {self.active_food.name}\n\n'
        else:
            out += f'**Active Food**: none\n\n'

        for slot in armour_print_order:
            item = self.all_armour[slot]
            out += f'**{string.capwords(slot)}**: '
            if item is not None:
                out += f'{item.name} '
                out += f'*(dam: {item.damage}, ' \
                       f'acc: {item.accuracy}, ' \
                       f'arm: {item.armour}, ' \
                       f'pray: {item.prayer})*\n'
            else:
                out += 'none *(dam: 0, acc: 0, arm: 0, pray: 0)*\n'

        return out

    def calc_xp_to_level(self, skill: str, level: int) -> int:
        """Calculates the xp needed to get to a level."""
        author_levels = self.skill_level_mapping
        author_xps = self.skill_xp_mapping

        if skill not in author_levels.keys():
            return f'{skill} is not a skill.'

        if level > 99:
            return f'You have already attained the maximum level in this skill.'

        current_xp = author_xps[skill]
        for xp_value in XP_TO_LEVEL_MAP.keys():
            if XP_TO_LEVEL_MAP[xp_value] == level:
                xp_needed = int(xp_value) - current_xp
                break
        else:
            raise KeyError
        return xp_needed

    @property
    def usable_prayers(self) -> List[Prayer]:
        prayers = Prayer.objects.filter(level_required__lte=self.prayer_level)
        ret = []
        for p in prayers:
            if p.quest_req and p.quest_req in self.completed_quests_list:
                ret.append(p)
            elif not p.quest_req:
                ret.append(p)

        return ret

    @property
    def completed_quests_list(self) -> List[Quest]:
        return [uq.quest for uq in self.userquest_set.all()]

    @property
    def num_quests_complete(self) -> int:
        return len(self.completed_quests_list)

    @property
    def is_eating(self) -> bool:
        return self.active_food is not None

    @property
    def max_possible_level(self) -> int:
        return 99 * len(self.level_fields)

    @staticmethod
    def _calc_level(xp) -> int:
        return xp_to_level(xp)

    @property
    def all_armour(self) -> Dict[str, Item]:
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
    def damage(self) -> int:
        damage = 0
        for item in self.equipment_slots:
            if item:
                damage += item.damage
        return damage

    @property
    def accuracy(self) -> int:
        accuracy = 0
        for item in self.equipment_slots:
            if item:
                accuracy += item.accuracy
        return accuracy

    @property
    def armour(self) -> int:
        armour = 0
        for item in self.equipment_slots:
            if item:
                armour += item.armour
        return armour

    @property
    def prayer_bonus(self) -> int:
        prayer_bonus = 0
        for item in self.equipment_slots:
            if item:
                prayer_bonus += item.prayer
        return prayer_bonus

    @property
    def equipment_stats(self) -> Tuple[int, int, int, int]:
        return self.damage, self.accuracy, self.armour, self.prayer_bonus

    @property
    def combat_level(self) -> int:
        return self._calc_level(self.combat_xp)

    @property
    def slayer_level(self) -> int:
        return self._calc_level(self.slayer_xp)

    @property
    def gather_level(self) -> int:
        return self._calc_level(self.gather_xp)

    @property
    def artisan_level(self) -> int:
        return self._calc_level(self.artisan_xp)

    @property
    def cook_level(self) -> int:
        return self._calc_level(self.cook_xp)

    @property
    def prayer_level(self) -> int:
        return self._calc_level(self.prayer_xp)

    @property
    def rc_level(self) -> int:
        return self._calc_level(self.rc_xp)

    @property
    def total_level(self) -> int:
        return sum(self.level_fields)

    @property
    def total_xp(self) -> int:
        return sum(self.xp_fields)

    @property
    def is_maxed(self) -> bool:
        return self.total_level == self.max_possible_level



    @property
    def plain_name(self) -> str:
        return self.name.split("#")[0]

    @property
    def clue_counts(self) -> List[Tuple[str, int]]:
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

    @property
    def mention(self) -> str:
        return f"<@{self.id}>"

    @property
    def display_name(self) -> str:
        return self.nick if self.nick else self.name

    def __repr__(self):
        return "User ID %d: %s" % (self.id, self.name)

    def __str__(self):
        return self.__repr__()
