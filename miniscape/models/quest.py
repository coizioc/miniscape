from django.db import models
from .item import Item

class Quest(models.Model):

    # TODO:
    # - Implement "quest unlocks item x"
    # - Test quest item requirements
    # - Test quest-on-quest requirements _lenny face_
    # - Test quest item rewards

    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=200,
                            unique=True)
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
    quest_req = models.ManyToManyField('self', blank=True)


class QuestItemRequirements(models.Model):
    class Meta:
        unique_together = (('quest', 'item'),)

    quest = models.ForeignKey(Quest,
                              on_delete=models.CASCADE)
    item = models.ForeignKey(Item,
                             on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=1)


class QuestItemRewards(models.Model):
    class Meta:
        unique_together = (('quest', 'item'),)

    quest = models.ForeignKey(Quest,
                              on_delete=models.CASCADE)
    item = models.ForeignKey(Item,
                             on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=1)
