# Generated by Django 2.1.2 on 2018-10-13 03:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('miniscape', '0006_user_items'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='userinventory',
            unique_together={('user', 'item')},
        ),
    ]