from cogs.helper import items
from config import RUNEID_FILE, VIS_FILE, VIS_SHOP_FILE

# The way ~vis works is that there are three slots for runes to fit. Each are randomly selected each day.
#
# The first slot is the same for everyone. The second slot can be one of three runes, which are the same for everyone.
# The third slot is a random rune unique to each person. Each slot has a second preference based on the same criteria.
# As the number of attempts increase, the number of runes needed to make the vis wax increases.
#
# The vis file is stored as list of length 9. Here is what each element in the list represents:
# * 0: first choice of first slot; same for everyone.
# * 1: second choice of first slot; same for everyone.
# * 2: first of three first choices of second slot; same for everyone.
# * 3: first of three second choices of second slot; same for everyone.
# * 4: second of three first choices of second slot; same for everyone.
# * 5: second of three second choices of second slot; same for everyone.
# * 6: third of three first choices of second slot; same for everyone.
# * 7: third of three second choices of second slot; same for everyone.
# * 8: the unix timestamp for the current date.

BASE_COST = 2500
VIS_DELTA = 250
