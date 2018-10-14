# Generated by Django 2.1.2 on 2018-10-13 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miniscape', '0014_auto_20181013_1958'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quest',
            name='quest_req',
        ),
        migrations.AddField(
            model_name='quest',
            name='quest_reqs',
            field=models.ManyToManyField(blank=True, related_name='quest_unlocks', to='miniscape.Quest'),
        ),
    ]