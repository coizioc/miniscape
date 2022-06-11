import logging
import random
from collections import Counter
from .item import Item

from django.db import models


class Monster(models.Model):

    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=200,
                            unique=True)
    plural = models.CharField(max_length=200,
                              blank=True,
                              default="s")
    nick = models.ManyToManyField('MonsterNickname')



    # Stats
    xp = models.PositiveIntegerField(default=0)
    slayer_level_req = models.PositiveIntegerField(default=0)
    damage = models.PositiveIntegerField(default=0)
    accuracy = models.PositiveIntegerField(default=0)
    armour = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)

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

    quest_req = models.ForeignKey('Quest',
                                  on_delete=models.SET_NULL,
                                  null=True)

    @classmethod
    def find_by_name_or_nick(cls, name: str):
        monster = Monster.objects.filter(name__iexact=name)
        if monster:
            return monster[0]
        else:
            nick = MonsterNickname.objects.filter(nickname__iexact=name)
            if nick:
                return nick[0].real_monster
            else:
                if name.endswith('s'):
                    return Monster.find_by_name_or_nick(name[:-1])
                else:
                    return None

    @property
    def rares(self):
        return self.monsterloot_set.filter(rarity__gt=256)

    @property
    def loot_table(self):
        return self.monsterloot_set.all()

    @property
    def alias_strings(self):
        nicknames = self.monsternickname_set.all().order_by('nickname')
        return [n.nickname for n in nicknames]

    @property
    def combat_stats(self):
        return self.damage, self.accuracy, self.armour, self.level

    def generate_loot(self, num, luck_factor):
        """Generates a Counter from a number of killed monsters"""
        loot_table = self.loot_table
        loot = Counter()
        logging.getLogger(__name__).info(f"Generating loot for {num} {self.name}. Luck factor: {luck_factor}")

        # Assign our always loots
        for ml in loot_table.filter(rarity=1):
            loot[ml.item] += num

        # Generate our loots
        possible_loots = loot_table.filter(rarity__gt=1)
        possible_loots = list(possible_loots)
        for _ in range(round(int(num) * 8 * luck_factor)):
            ml = random.sample(possible_loots, 1)[0]
            item_chance = ml.rarity
            if random.randint(1, item_chance) == 1 and item_chance > 1:
                amount = random.randint(ml.min_amount, ml.max_amount)
                log_str = "Awarded %d %s as part of loot generation for %d %s" % (amount,
                                                                                  ml.item.name,
                                                                                  int(num),
                                                                                  self.name)
                logging.getLogger(__name__).info(log_str)
                loot[ml.item] += amount

            # Chance to drop christmas cracker per kill for Christmas event.
            if random.randint(1, 100000) == 1:
                christmas_cracker = Item.objects.get(name='christmas cracker')
                log_str = "Awarded %d %s as part of loot generation for %d %s" % (1,
                                                                                  christmas_cracker.name,
                                                                                  int(num),
                                                                                  self.name)
                logging.getLogger(__name__).info(log_str)
                loot[christmas_cracker] += 1

        return loot

    def pluralize(self, number, with_zero=False):
        # TODO: Make this do something I guess
        return "%s %s" % (str(number), self.name)

    def __repr__(self):
        return "Monster ID %d: %s" % (self.id, self.name)

    def __str__(self):
        return self.__repr__()


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

    def __repr__(self):
        return "MonsterLoot for monster %s and item %s" % (self.monster, self.item)

    def __str__(self):
        return self.__repr__()


class MonsterNickname(models.Model):
    class Meta:
        unique_together = (('nickname', 'real_monster'),)

    real_monster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=200,
                                unique=True)

    def __repr__(self):
        return "Nickname for Monster (%s), nickname: %s" % (str(self.real_monster), self.nickname)

    def __str__(self):
        return self.__repr__()
