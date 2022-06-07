NAME_KEY = 'name'                       # Name of prayer, stored as a string.
NICK_KEY = 'nick'                       # List of nicknames of prayer.
DESC_KEY = 'description'                # Description of function of prayer.
PRAYER_KEY = 'prayer'                   # Prayer requirement.
DRAIN_KEY = 'drain'                     # Drain rate for prayer.
DAMAGE_KEY = 'damage'                   # Percent damage increase for prayer.
ACCURACY_KEY = 'accuracy'               # Percent accuracy increase for prayer.
ARMOUR_KEY = 'armour'                   # Percent armour increase for prayer.
CHANCE_KEY = 'chance'                   # Percent chance increase for prayer.
FACTOR_KEY = 'factor'                   # Factor multiplier increase for prayer.
KEEP_FACTOR_KEY = 'keepfactorondeath'   # Boolean whether factor can be kept on death.
GATHER_KEY = 'gather'                   # Factor of gather time decrease for prayer.
AFFINITY_KEY = 'aff'                    # Int representing the kinds of monsters the prayer works against.
QUEST_KEY = 'quest'                     # Quest requirement for prayer.

DEFAULT_PRAYER = {
    NAME_KEY: 'unknown prayer',
    NICK_KEY: [],
    DESC_KEY: 'unknown description',
    PRAYER_KEY: 1,
    DRAIN_KEY: 100,
    DAMAGE_KEY: 0,
    ACCURACY_KEY: 0,
    ARMOUR_KEY: 0,
    CHANCE_KEY: 0,
    FACTOR_KEY: 1,
    KEEP_FACTOR_KEY: False,
    GATHER_KEY: 1,
    QUEST_KEY: -1
}





