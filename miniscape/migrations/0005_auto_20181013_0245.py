# Generated by Django 2.1.2 on 2018-10-13 02:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miniscape', '0004_auto_20181013_0204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='affinity',
            field=models.PositiveIntegerField(choices=[(0, 'Melee'), (1, 'Range'), (2, 'Magic')], default=None, null=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='affinity',
            field=models.PositiveIntegerField(choices=[(0, 'Melee'), (1, 'Range'), (2, 'Magic')], default=0),
        ),
    ]