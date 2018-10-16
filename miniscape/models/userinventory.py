from django.db import models


class UserInventory(models.Model):
    class Meta:
        unique_together = (('user', 'item'),)

    user = models.ForeignKey('User',
                             on_delete=models.CASCADE)

    item = models.ForeignKey('Item',
                             on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=1)
    is_locked = models.BooleanField(default=False)


    @property
    def total_value(self):
        return self.amount * self.item.value

    def __repr__(self):
        return "UserInventory User (%s) / Item (%s) / Amount: %d" % (self.user, self.item, self.amount)

    def __str__(self):
        return self.__repr__()
