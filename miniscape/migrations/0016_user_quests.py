# Generated by Django 2.1.2 on 2018-10-14 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miniscape', '0015_auto_20181013_2112'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='quests',
            field=models.ManyToManyField(to='miniscape.Quest'),
        ),
    ]
