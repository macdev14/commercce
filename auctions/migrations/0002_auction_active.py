# Generated by Django 4.0.3 on 2022-07-12 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Active'),
        ),
    ]
