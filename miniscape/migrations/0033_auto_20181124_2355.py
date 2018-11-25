# Generated by Django 2.1.2 on 2018-11-25 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miniscape', '0032_auto_20181016_2017'),
    ]

    operations = [
        migrations.CreateModel(
            name='PeriodicChecker',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('last_check_datetime', models.DateTimeField(auto_now_add=True, verbose_name='last_check')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='is_mod',
            field=models.BooleanField(default=False),
        ),
    ]
