# Generated by Django 2.1.2 on 2018-10-14 01:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('miniscape', '0021_auto_20181014_0114'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClueLoot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_amount', models.PositiveIntegerField(default=1)),
                ('max_amount', models.PositiveIntegerField(default=1)),
                ('rarity', models.PositiveIntegerField(default=1)),
                ('clue_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clue_item', to='miniscape.Item')),
                ('loot_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loot_item', to='miniscape.Item')),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='clue_loot',
            field=models.ManyToManyField(through='miniscape.ClueLoot', to='miniscape.Item'),
        ),
    ]