from django.db import models


class ClueLoot(models.Model):
    class Meta:
        unique_together = (('clue_item', 'loot_item'),)

    clue_item = models.ForeignKey('Item',
                                  on_delete=models.CASCADE,
                                  related_name='clue_item')

    loot_item = models.ForeignKey('Item',
                                  on_delete=models.CASCADE,
                                  related_name='loot_item')

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
