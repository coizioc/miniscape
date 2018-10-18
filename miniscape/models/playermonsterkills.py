from django.db import models


class PlayerMonsterKills(models.Model):
    class Meta:
        unique_together = (('user', 'monster'),)

    user = models.ForeignKey('User',
                             on_delete=models.CASCADE)

    monster = models.ForeignKey('Monster',
                                on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=1)

    def __repr__(self):
        return "MonsterKills object. Monster: %s. Player: %s. Amt: %d" % (self.monster, self.user, self.amount)

    def __str__(self):
        return self.__repr__()