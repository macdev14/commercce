from typing import List
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=100)
    #auction = models.ManyToManyField(Auction, blank=True, related_name="auctionCategory")
    def __str__(self):
        return f"{self.name} - {self.description}"

class Auction(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank = False)
    price = models.IntegerField()
    current_bid = models.IntegerField(default=0)
    number_bid = models.IntegerField(default=0)
    photo = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctioneer")
    category = models.ForeignKey(Category, blank=True, related_name="listcategory", on_delete=models.CASCADE)
    active = models.BooleanField(verbose_name='Active', default=True)
    winner = models.ForeignKey(User, blank=True, null=True, related_name="winner", on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.name} - {self.price}"
    

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, default=0, related_name="list" )
    price = models.IntegerField(verbose_name="Bid")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    
    def save(self, *args, **kwargs):
        self.auction.winner = self.user
        self.auction.save()
        super(Bid, self).save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.auction.name} - {self.price}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userReference")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="listingReference")
    content = models.CharField(max_length=500)
    def __str__(self):
        return f"{self.name.first_name} - {self.auction.name}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userReferenceWatchlist")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="listingReferenceWatchlist")
    def __str__(self):
        return f"{self.user.first_name} - {self.auction.name}"


