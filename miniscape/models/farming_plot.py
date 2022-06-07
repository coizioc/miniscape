from django.db import models
from django.utils import timezone


class Patch:
    def __init__(self, name, identifier):
        self.identifier: int = identifier
        self.name: str = name


ALLOTMENT_PATCH = Patch("allotment patch", 1)
HERB_PATCH = Patch("herb patch", 2)
TREE_PATCH = Patch("tree patch", 3)
FRUIT_TREE_PATCH = Patch("fruit tree patch", 4)
BUSH_PATCH = Patch("bush patch", 5)
FLOWER_PATCH = Patch("flower patch", 6)

type_choices = (
    (ALLOTMENT_PATCH.identifier, ALLOTMENT_PATCH.name),
    (HERB_PATCH.identifier, HERB_PATCH.name),
    (TREE_PATCH.identifier, TREE_PATCH.name),
    (FRUIT_TREE_PATCH.identifier, FRUIT_TREE_PATCH.name),
    (BUSH_PATCH.identifier, BUSH_PATCH.name),
    (FLOWER_PATCH.identifier, FLOWER_PATCH.name)
)


class FarmPlot(models.Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=200,
                            blank=True,
                            default="")
    nick = models.CharField(max_length=200,
                            blank=True,
                            default="",
                            null=True)

    type = models.PositiveIntegerField(choices=type_choices,
                                           default=ALLOTMENT_PATCH.identifier)

    quest_req = models.ForeignKey('Quest',
                                  on_delete=models.SET_NULL,
                                  null=True)

    def __repr__(self):
        return f'FarmPlot "{self.nick}"; ID: {self.id}; type: {type_choices[self.type][1]}'

    def __str__(self):
        return self.__repr__()


class UserFarmPlot(models.Model):
    class Meta:
        unique_together = (('user', 'plot'),)

    plot = models.ForeignKey('FarmPlot',
                             on_delete=models.CASCADE)
    user = models.ForeignKey('User',
                             on_delete=models.CASCADE)
    seed = models.ForeignKey('Item',
                             on_delete=models.CASCADE)
    time_planted = models.DateTimeField(auto_now_add=True)
    time_last_harvested = models.DateTimeField(default=timezone.now)
