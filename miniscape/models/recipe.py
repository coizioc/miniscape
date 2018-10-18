
from django.db import models


class Recipe(models.Model):

    creates = models.ForeignKey('Item',
                                related_name="item_creates",
                                on_delete=models.CASCADE)
    skill_requirement = models.CharField(max_length=200,
                                         default="artisan")
    level_requirement = models.PositiveIntegerField(default=0)
    item_requirements = models.ManyToManyField('Item',
                                               through='RecipeRequirement',
                                               through_fields=('recipe', 'item'))

    quest_requirement = models.ForeignKey('Quest',
                                          on_delete=models.SET_NULL,
                                          null=True)

    def get_requirements(self):
        return self.reciperequirement_set.all().order_by('item__name')

    def __repr__(self):
        return "Recipe for item %s" % self.creates

    def __str__(self):
        return self.__repr__()


class RecipeRequirement(models.Model):
    class Meta:
        unique_together = (('recipe', 'item'),)

    recipe = models.ForeignKey('Recipe',
                               on_delete=models.CASCADE)

    item = models.ForeignKey('Item',
                             on_delete=models.CASCADE)

    amount = models.PositiveIntegerField(default=1)

    def __repr__(self):
        return "RecipeRequirement for recipe (%s), item (%s), amount (%d)" % (self.recipe, self.item, self.amount)

    def __str__(self):
        return self.__repr__()
