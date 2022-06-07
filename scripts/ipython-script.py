import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "miniscapebot.settings")
import django
django.setup()
from miniscape.models import *
from django.db.models import Q

me = User.objects.get(pk=147501762566291457)
ca = Quest.objects.get(name__iexact="cook's assistant")
bronze_sword = Item.objects.get(name__iexact="bronze sword")
chicken = Monster.objects.get(name__iexact="chicken")
bronze_sword_recipe = Recipe.objects.filter(creates=bronze_sword)
