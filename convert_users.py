#! /usr/bin/env python

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE","mathbot.settings")
import django
django.setup()

import ujson
from miniscape.models import User, Item, UserInventory, ItemNickname
import config

userid = 147501762566291457
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
def load_alan():
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
                    pray_xp=u['pray'],
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

        for k,v in u['items'].items():
            locked = k in u['locked']

            if not UserInventory.objects.get(user=user, item=Item.objects.get(id=k)):
                inv = UserInventory(user = user,
                                    item = Item.objects.get(id=k),
                                    amount=v,
                                    is_locked= locked)
                inv.save()
            else:
                print("Object already exists: %s" % UserInventory.objects.get(user=user, item=Item.objects.get(id=k)))
            pass


item_json = config.ITEM_JSON
def load_items():
    with open(item_json, 'r', encoding='utf-8-sig') as f:
        ITEMS = ujson.load(f)
        item_list = []
        for k,v in ITEMS.items():
            v = item_dict(v)
            k = int(k)
            qs = Item.objects.filter(id=k)

            i = Item(id=k,
                     name=v['name'],
                     plural=v['plural'] if v['plural'] else '',
                     value=v['value'],
                     damage=v['damage'],
                     accuracy=v['accuracy'],
                     armour=v['armour'],
                     prayer=v['prayer'],
                     slot=v['slot'],
                     level=v['level'],
                     xp=v['xp'],
                     affinity=v['aff'],
                     is_gatherable=v['gather'],
                     is_tree=v['tree'],
                     is_rock=v['rock'],
                     is_fish=v['fish'],
                     is_pot=v['potion'],
                     is_rune=v['rune'],
                     is_cookable=v['cook'],
                     is_buryable=v['bury'],
                     is_max_only=v['max'],
                     is_pet=v['pet'],
                     pouch=v['pouch'],
                     luck_modifier=v['luck']
                     )
            i.save(force_update=bool(qs))
            if v['nick']:
                for n in v['nick']:
                    qs = ItemNickname.objects.filter(nickname=n)
                    nick = None
                    if qs:
                        nick = qs[0]
                        nick.item=i
                        nick.nickname=n
                    else:
                        nick = ItemNickname(item=i,
                                            nickname=n)
                    nick.save()
                    pass


def load_recipes():
    from config import RECIPE_JSON, XP_FACTOR
    from miniscape.models.recipe import Recipe, RecipeRequirement

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
            print('wut')

        # if
        r = Recipe(creates=created_item,
                   skill_requirement=skill,
                   level_requirement=v[skill],
                   )
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
        q = Quest(id=k,
                  name=v['name'],
                  descrition=v['description'],
                  success=v['success'],
                  failure=v['failure'],
                  damage=v['damage'],
                  accurac=v['accuracy'],
                  armour=v['armour'],
                  level=v['level'],
                  time=v['time'],
                  has_dragon=v['dragon']
                  )
        q.save()

        if v['quest req']:
            for req in v['quest req']
                q.quest_req = Quest.objects.get(id=req)


        if v['item_req']:
            for qid,amt in v['item_req'].items()
                qir = QuestItemRequirements(quest=q,
                                            item=Item.objects.get(id=qid),
                                            amount=amt)
                qir.save()

        if v['reward']:


if __name__ == '__main__':
    load_quests()
    #load_items()
    #load_alan()
    load_recipes()
    pass
