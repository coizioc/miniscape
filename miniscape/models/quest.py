from django.db import models
from .item import Item


class Quest(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=200,
                            unique=True)
    nick = models.ManyToManyField('QuestNickname')

    description = models.CharField(max_length=40960,
                                   default="Go something for this person "
                                           "and get some stuff in return.")
    success = models.CharField(max_length=4096,
                               default="You did it!")
    failure = models.CharField(max_length=4096,
                               default="You didn't do it!")

    # Stats
    damage = models.PositiveIntegerField(default=0)
    accuracy = models.PositiveIntegerField(default=0)
    armour = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=0)
    time = models.PositiveIntegerField(default=0)

    # Booleans
    has_dragon = models.BooleanField(default=False)

    # Relationships
    quest_reqs = models.ManyToManyField('self',
                                        blank=True,
                                        related_name='quest_unlocks',
                                        symmetrical=False)

    @property
    def combat_stats(self):
        return self.damage, self.accuracy, self.armour, self.level

    @property
    def required_items(self):
        return self.questitemrequirements_set.all()

    @property
    def reward_items(self):
        return self.questitemrewards_set.all()

    def __repr__(self):
        return "Quest: %s" % self.name

    def __str__(self):
        return self.__repr__()


class UserQuest(models.Model):
    class Meta:
        unique_together = (('quest', 'user'),)

    quest = models.ForeignKey(Quest,
                              on_delete=models.CASCADE)
    user = models.ForeignKey('User',
                             on_delete=models.CASCADE)


class QuestItemRequirements(models.Model):
    class Meta:
        unique_together = (('quest', 'item'),)

    quest = models.ForeignKey(Quest,
                              on_delete=models.CASCADE)
    item = models.ForeignKey(Item,
                             on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=1)

    def __repr__(self):
        return "QuestItemRequirements for Quest (%s), item: %s (%d)" % (self.quest, self.item, self.amount)

    def __str__(self):
        return self.__repr__()


class QuestItemRewards(models.Model):
    class Meta:
        unique_together = (('quest', 'item'),)

    quest = models.ForeignKey(Quest,
                              on_delete=models.CASCADE)
    item = models.ForeignKey(Item,
                             on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=1)

    def __repr__(self):
        return "QuestItemRewards for Quest (%s), item: %s (%d)" % (self.quest, self.item, self.amount)

    def __str__(self):
        return self.__repr__()


class QuestNickname(models.Model):
    class Meta:
        unique_together = (('nickname', 'real_quest'),)

    real_quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=200,
                                unique=True)

    def __repr__(self):
        return "Nickname for Quest (%s), nickname: %s" % (str(self.real_quest), self.nickname)

    def __str__(self):
        return self.__repr__()
