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


class FarmRecipe(models.Model):
    creates = models.ForeignKey('Item',
                                related_name="item_creates",
                                on_delete=models.CASCADE)
    level_requirement = models.PositiveIntegerField(default=0)
    seed_requirement = models.ForeignKey('Item',
                                         related_name="item_creates",
                                         on_delete=models.CASCADE)
    # How long it takes the plant to grow
    growth_time_minutes = models.PositiveIntegerField(null=False,
                                                      default=60)

    # If it's a wood tree, it doesn't give fruit or deplete. It gives a certain number of logs
    log_yield = models.PositiveIntegerField(null=False,
                                            default=0)

    # How long it takes the individual fruits to regrow. 0 means it doesn't regrow
    fruit_growth_time_minutes = models.PositiveIntegerField(null=False,
                                                            default=0)

    # Maximum number of fruits that can be on the tree or bush. Only relevant if fruit_growth_time_minutes is >0
    max_fruits = models.PositiveIntegerField(null=False,
                                             default=60)

    # Depletion chance specifies the odds of a "depletion" being consumed every pick. A lower depletion chance or higher
    # number of depletions means a bigger harvest. If set 0, means it's a fruit bearing plant and uses static numbers
    depletion_chance = models.PositiveIntegerField(null=False,
                                                   default=0)
    depletions = models.PositiveIntegerField(null=False,
                                             default=0)


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
