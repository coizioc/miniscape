from django.db import models


class Preset(models.Model):
    class Meta:
        unique_together=(("user", "name"),)

    user = models.ForeignKey('User',
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=200,
                            blank=True,
                            default="")

    # Armour
    head_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="preset_head")
    back_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="preset_back")
    neck_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="preset_neck")
    ammo_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="preset_ammo")
    mainhand_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="preset_mainhand")
    torso_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="preset_torso")
    offhand_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="preset_offhand")
    legs_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="preset_legs")
    hands_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="preset_hands")
    feet_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="preset_feet")
    ring_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="preset_ring")
    pocket_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="preset_pocket")
    hatchet_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="preset_hatchet")
    pickaxe_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="preset_pickaxe")

    # Boosts
    potion_slot = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="preset_potion")
    prayer_slot = models.ForeignKey('Prayer', on_delete=models.SET_NULL, null=True)
    active_food = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, related_name="preset_food")
