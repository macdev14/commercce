# Generated by Django 4.0.2 on 2022-03-24 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0010_bid_auction'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='current_bid',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='bid',
            name='price',
            field=models.IntegerField(verbose_name='Bid'),
        ),
    ]
