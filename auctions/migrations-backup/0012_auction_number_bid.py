# Generated by Django 4.0.2 on 2022-03-24 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_auction_current_bid_alter_bid_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='number_bid',
            field=models.IntegerField(default=0),
        ),
    ]
