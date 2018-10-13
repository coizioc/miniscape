from django.db import models


class PlayerMonsterKills(models.Model):
    class Meta:
        unique_together = (('user', 'monster'),)

    user = models.ForeignKey('User',
                             on_delete=models.CASCADE)

    monster = models.ForeignKey('Monster',
                                on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=1)
