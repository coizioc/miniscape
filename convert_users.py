#! /usr/bin/env python

import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE","mathbot.settings")
import django
django.setup()

import ujson
from miniscape.models.monster import MonsterNickname

from miniscape.models import User, Item, UserInventory, ItemNickname, Quest, Prayer, PrayerNickname
import config
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from miniscape.models.quest import UserQuest


USER_DIRECTORY = config.USER_DIRECTORY

class safe_dict:
    def __init__(self, dict):
        self.d = dict

    def __getitem__(self, key):
        try:
            return self.d[key]
        except KeyError:
            return None


class item_dict:
    def __init__(self, dict):
        self.d = dict

    def __getitem__(self, item):
        try:
            return self.d[item]
        except KeyError:
            return 0


class quest_dict:
    def __init__(self, dict):
        self.d = dict

    def __getitem__(self, item):
        try:
            return self.d[item]
        except KeyError:
            if item in ['name', 'description', 'success', 'failure']:
                return ''
            return 0


def load_users():
    userids = [116380350296358914, 147501762566291457, 293219528450637824, 132049789461200897]
    for userid in userids:
        with open(f'{USER_DIRECTORY}{userid}.json', 'r+') as f:
            u = safe_dict(ujson.load(f))

            clues = safe_dict(u['clues'])
            easy_clues = clues['1'] if clues['1'] else 0
            med_clues = clues['2'] if clues['2'] else 0
            hard_clues = clues['3'] if clues['3'] else 0
            elite_clues = clues['4'] if clues['4'] else 0
            master_clues = clues['5'] if clues['5'] else 0
            user = User(id=userid,
                        name="",
                        combat_xp=u['combat'],
                        slayer_xp=u['slayer'],
                        artisan_xp=u['artisan'],
                        cook_xp=u['cook'],
                        gather_xp=u['gather'],
                        pray_xp=u['prayer'],
                        rc_xp=u['runecrafting'],
                        easy_clues=easy_clues,
                        medium_clues=med_clues,
                        hard_clues=hard_clues,
                        elite_clues=elite_clues,
                        master_clues=master_clues,
                        is_ironman=u['ironman'],
                        is_reaper_complete=u['reaperdone'],
                        is_vis_complete=u['vis'],
                        vis_attempts=u['visattempts'],
                        )
            user.save()
            # TODO
            # Set active prayer
            # prayer = Prayer.objects.get(id=)

            hex_number = int(str(u['quests'])[2:], 16)
            binary_number = str(bin(hex_number))[2:]
            completed_quests = []
            for bit in range(len(binary_number)):
                if binary_number[bit] == '1':
                    completed_quests.append(len(binary_number) - bit)

            # Add quests
            for q in completed_quests:
                uq = UserQuest.objects.get_or_create(user=user,
                                                     quest=Quest.objects.get(id=q))[0]
                uq.save()
            user.save()

            # Add items
            for k,v in u['items'].items():
                locked = k in u['locked']
                try:
                    inv = UserInventory.objects.update_or_create(user=user,
                                                                 item=Item.objects.get(id=k),
                                                                 defaults={'amount':v,'is_locked':locked})
                                                                 # amount=v,
                                                                 # is_locked=locked)
                    pass
                except IntegrityError as e:
                    pass


            # Add killed monsters
            try:
                monsters = u['monsters']
            except KeyError:
                monsters = None
            if monsters:
                from miniscape.models import PlayerMonsterKills, Monster
                for monster, num in monsters.items():
                    pmk = PlayerMonsterKills.objects.update_or_create(user=user,
                                                                      monster=Monster.objects.get(id=monster),
                                                                      amount=num)

            # Add Equipment
            try:
                equipment = u['equip']
            except KeyError:
                equipment = None

            if equipment:
                for slot, item in equipment.items():
                    #ugh
                    if int(item) == -1:
                        continue

                    try:
                        item_obj = Item.objects.get(id=int(item))
                    except ObjectDoesNotExist as e:
                        pass

                    slot = int(slot)
                    if slot == 1:
                        user.head_slot = item_obj
                    elif slot == 2:
                        user.back_slot = item_obj
                    elif slot == 3:
                        user.neck_slot = item_obj
                    elif slot == 4:
                        user.ammo_slot = item_obj
                    elif slot == 5:
                        user.mainhand_slot = item_obj
                    elif slot == 6:
                        user.torso_slot = item_obj
                    elif slot == 7:
                        user.offhand_slot = item_obj
                    elif slot == 8:
                        user.legs_slot = item_obj
                    elif slot == 9:
                        user.hands_slot = item_obj
                    elif slot == 10:
                        user.feet_slot = item_obj
                    elif slot == 11:
                        user.ring_slot = item_obj
                    elif slot == 12:
                        user.pocket_slot = item_obj
                    elif slot == 13:
                        user.hatchet_slot = item_obj
                    elif slot == 14:
                        user.pickaxe_slot = item_obj
                    elif slot == 15:
                        user.potion_slot = item_obj

                    user.save()


item_json = config.ITEM_JSON


def load_items(quests_unlocks=False):
    with open(item_json, 'r', encoding='utf-8-sig') as f:
        ITEMS = ujson.load(f)
        for k, v in ITEMS.items():
            v = item_dict(v)
            k = int(k)
            i = Item.objects.get_or_create(id=k)[0]

            if quests_unlocks:
                x = v['quest req']
                if x:
                    quest = Quest.objects.get(id=x)
                    i.quest_req = quest
                    i.save()
                    pass
                else:
                    pass
            else:
                i.name = v['name']
                i.plural = v['plural'] if v['plural'] else ''
                i.value = v['value']
                i.damage = v['damage']
                i.accuracy = v['accuracy']
                i.armour = v['armour']
                i.prayer = v['prayer']
                i.slot = v['slot']
                i.level = v['level']
                i.xp = v['xp']
                i.affinity = v['aff']
                i.is_gatherable = v['gather']
                i.is_tree = v['tree']
                i.is_rock = v['rock']
                i.is_fish = v['fish']
                i.is_pot = v['potion']
                i.is_rune = v['rune']
                i.is_cookable = v['cook']
                i.is_buryable = v['bury']
                i.is_max_only = v['max']
                i.is_pet = v['pet']
                i.food_value = v['eat']
                i.pouch = v['pouch']
                i.luck_modifier = v['luck']
                i.save()

                if v['nick']:
                    for n in v['nick']:
                        nick = ItemNickname.objects.get_or_create(real_item=i,
                                                                  nickname=n)[0]
                        nick.item = i
                        nick.nickname = n
                        nick.save()
                        pass


def load_recipes():
    from config import RECIPE_JSON, XP_FACTOR
    from miniscape.models.recipe import Recipe, RecipeRequirement
    from miniscape.models.quest import Quest

    with open(RECIPE_JSON, 'r') as f:
        RECIPES = ujson.load(f)

    for k,v in RECIPES.items():
        created_item = Item.objects.get(id=k)

        if 'artisan' in v.keys():
            skill = 'artisan'
        elif 'cook' in v.keys():
            skill = 'cook'
        elif 'runecrafting' in v.keys():
            skill = 'rc'
        else:
            v['artisan'] = 1
            skill = 'artisan'



        try:
            quest_req = Quest.objects.get(id=v['quest req'][0])
        except KeyError:
            quest_req = None
        r = Recipe.objects.get_or_create(creates=created_item)[0]
        r.skill_requirement=skill
        r.level_requirement=v[skill]
        r.quest_requirement = quest_req

        r.save()
        for itemid, amt in v['inputs'].items():
            rr = RecipeRequirement(recipe=r,
                                   item = Item.objects.get(id=itemid),
                                   amount=amt)
            rr.save()
        pass

def load_quests():
    from config import RECIPE_JSON, XP_FACTOR, QUESTS_JSON
    from miniscape.models.quest import Quest, QuestItemRewards, QuestItemRequirements

    with open(QUESTS_JSON, 'r') as f:
        quests = ujson.load(f)


    for k,v in quests.items():
        v = quest_dict(v)
        q = Quest.objects.get_or_create(id=k)[0]
        q.name = v['name']
        q.description = v['description']
        q.success = v['success']
        q.failure = v['failure']
        q.damage = v['damage']
        q.accuracy = v['accuracy']
        q.armour = v['armour']
        q.level = v['level']
        q.time = v['time']
        q.has_dragon = v['dragon']
        q.save()

    for k,v in quests.items():
        v = quest_dict(v)
        q = Quest.objects.get(id=k)
        if v['quest req']:
            for req in v['quest req']:
                q.quest_reqs.add(Quest.objects.get(id=req))
                q.save()

        if v['item req']:
            for qid, amt in v['item req'].items():
                qir = QuestItemRequirements.objects.update_or_create(quest=q,
                                                                     item=Item.objects.get(id=qid),
                                                                     amount=amt)
                qir[0].save()

        if v['reward']:
            for itemid, amt in v['reward'].items():
                qir = QuestItemRewards.objects.update_or_create(quest=q,
                                                                item=Item.objects.get(id=itemid),
                                                                amount=amt)
                qir[0].save()
            pass


class monster_dict:
    def __init__(self, dict):
        self.d = dict

    def __getitem__(self, item):
        try:
            return self.d[item]
        except KeyError:
            if item in ['name', 'plural']:
                return ''
            return 0

def load_monsters():
    from config import MONSTER_DIRECTORY, MONSTERS_JSON
    from miniscape.models import Monster, MonsterLoot
    with open(MONSTERS_JSON, 'r') as f:
        monsters = ujson.load(f)

    for monsterid, monster in monsters.items():
        m = monster_dict(monster)
        monster = Monster.objects.update_or_create(id=monsterid,
                                                   name=m['name'],
                                                   plural=m['plural'],
                                                   xp=m['xp'],
                                                   slayer_level_req=m['slayer req'],
                                                   damage=m['damage'],
                                                   accuracy=m['accuracy'],
                                                   armour=m['armour'],
                                                   is_slayable=m['slayer'],
                                                   is_boss=m['boss'],
                                                   is_dragon=m['dragon'],
                                                   min_assignable=m['task_min'],
                                                   max_assignable=m['task_max'],
                                                   affinity=m['aff'],
                                                   )[0]
        monster.level = m['level']
        monster.save()
        pass

        # Load Quest requirements
        if m['quest req']:
            monster.quest_req = Quest.objects.get(id=m['quest req'])
            monster.save()

        if m['nick']:
            for nick in m['nick']:
                mn = MonsterNickname.objects.update_or_create(real_monster=monster,
                                                              nickname=nick)[0]
                mn.save()

    # Load the loot in
    from django.db.utils import IntegrityError
    for monster in Monster.objects.all():
        with open(MONSTER_DIRECTORY + str(monster.id) + '.txt', 'r') as f:
            loot = f.readlines()
            loot.sort()
        for line in loot:
            line = line.split(';')
            try:
                ml = MonsterLoot.objects.update_or_create(item=Item.objects.get(id=line[0]),
                                                          monster=monster,
                                                          min_amount=line[1],
                                                          max_amount=line[2],
                                                          rarity=line[3])
                ml[0].save()
            except IntegrityError as e:
                raise e


def get_clue_item_from_difficulty(diff: int):
    if diff == 1:
        return Item.objects.get(name="easy clue scroll")
    if diff == 2:
        return Item.objects.get(name="medium clue scroll")
    if diff == 3:
        return Item.objects.get(name="hard clue scroll")
    if diff == 4:
        return Item.objects.get(name="elite clue scroll")
    if diff == 5:
        return Item.objects.get(name="master clue scroll")


def load_clue_loot():
    from config import CLUES_DIRECTORY
    from miniscape.models import ClueLoot

    for i in [1,2,3,4,5]:
        with open(CLUES_DIRECTORY + str(i) + '.txt', 'r') as f:
            loot = f.readlines()
            loot.sort()

        for line in loot:
            line = line.split(';')
            cl = ClueLoot.objects.update_or_create(loot_item=Item.objects.get(id=line[0]),
                                                   clue_item=get_clue_item_from_difficulty(i))[0]

            cl.min_amount=line[1]
            cl.max_amount=line[2]
            cl.rarity=line[3]
            cl.save()


class prayer_dict:
    def __init__(self, dict):
        self.d = dict

    def __getitem__(self, item):
        try:
            ret = self.d[item]
            return ret
        except KeyError:
            if item in ['name', 'plural']:
                return ''
            return 0


def load_prayers():
    from config import PRAYERS_JSON
    with open(PRAYERS_JSON, 'r') as f:
        prayers = ujson.load(f)

    for k, v in prayers.items():
        v = prayer_dict(v)
        p = Prayer.objects.get_or_create(name=v['name'],
                                            id=int(k))[0]
        p.description=v['description']
        p.level_required=v['prayer']
        p.drain=v['drain']
        p.damage=v['damage']
        p.accuracy=v['accuracy']
        p.armour=v['armour']
        p.chance=v['chance']
        p.luck_factor=v['factor']
        p.affinity=v['affinity']
        p.gather=v['gather']
        p.save()

        # MAke the quest reqs
        if v['quest']:
            quest = Quest.objects.get(id=v['quest'])
            p.quest_req = quest
            p.save()

        if v['nick']:
            for nick in v['nick']:
                pn = PrayerNickname.objects.get_or_create(real_prayer=p,
                                    nickname=nick)[0]
                pn.save()


if __name__ == '__main__':
    # load_items()
    # load_quests()
    # load_items(quests_unlocks=True)
    # load_monsters()
    # load_clue_loot()
    # load_prayers()
    load_recipes()
    # load_users()

    pass
