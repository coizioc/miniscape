# Generated by Django 2.1.2 on 2018-10-13 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miniscape', '0008_auto_20181013_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='nick',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]