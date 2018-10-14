from django.db import models


class ClueLoot(models.Model):

    clue_item = models.ForeignKey('Item',
                                  on_delete=models.CASCADE,
                                  related_name='clue_item')

    loot_item = models.ForeignKey('Item',
                                  on_delete=models.CASCADE,
                                  related_name='loot_item')

    min_amount = models.PositiveIntegerField(default=1)
    max_amount = models.PositiveIntegerField(default=1)
    rarity = models.PositiveIntegerField(default=1)
