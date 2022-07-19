from unicodedata import category
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from string import Template
from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from django import forms
from django.contrib.auth.decorators import login_required

import auctions
from .models import Category, Comment, User, Auction, Bid, Watchlist
from django.contrib import messages

from django.template.defaulttags import register

@register.filter

def number_bids(auction):
    return Bid.objects.filter(auction=auction).count()


def in_watchlist(user_id,auction_id):
    return Watchlist.objects.filter(user__pk=user_id, auction__pk=auction_id).exists()
    

def index(request):
    auctions = Auction.objects.filter(active=True)
    user_id = request.user.id
    
    return render(request, "auctions/index.html", {
        "auctions" : auctions,
        "user_id" : user_id
    })
 
def category(request, category_id):
    if not Category.objects.filter(pk=category_id).exists():
         return render(request, "auctions/error.html", {
        "text" : "Category",
       
    })
    
    category = Category.objects.get(pk=category_id)
    auctions = Auction.objects.filter(category=category, active=True)
    user_id = request.user.id
    
    return render(request, "auctions/index.html", {
        "category": category.name,
        "auctions" : auctions,
        "user_id" : user_id
    })
 
def all_category(request):
    categories = Category.objects.all()
    return render(request, "auctions/category.html", {
        
        "categories" : categories
    })
 

@login_required
def watchlist(request): 
    watchlist = Watchlist.objects.filter(user=request.user, auction__active=True)
    return render(request, "auctions/watchlist.html", {
        "watchlist" : watchlist,
       
    })

@login_required
def winning(request): 
    auctions = Auction.objects.filter(winner=request.user)
    return render(request, "auctions/winner.html", {
        "auctions" : auctions,
       
    })


@login_required
def watchlist_add(request, auction_id):
    print(request)
    # if request.method == "POST":
    auctionId = auction_id
    print("auction id", auctionId)
    

    auction = Auction.objects.get(pk=auctionId)
    if not auction.active:
        messages.error(request, 'Auction already closed')
        return HttpResponseRedirect(reverse("place_bid", args=(auction_id,) ))
    if not Watchlist.objects.filter(auction=auction, user=request.user).exists():
        watchlist = Watchlist.objects.create(auction=auction, user=request.user)
        watchlist.save()
        messages.success(request, 'Added to watchlist')
    else:
        messages.error(request, 'Already added to watchlist')
        
    watchlist_filter = Watchlist.objects.filter(user=request.user)
    print(watchlist_filter)
    return HttpResponseRedirect(reverse("place_bid", args=(auction_id,) ))

@login_required
def watchlist_delete(request, auction_id):
    watchlist = Watchlist.objects.filter(user=request.user, auction__pk=auction_id).exists()
    if watchlist: 
        Watchlist.objects.filter(user=request.user, auction__pk=auction_id).delete()
        messages.success(request, 'Removed from watchlist')
    if not watchlist: messages.error(request, 'Could not Delete from watchlist')    
    return HttpResponseRedirect(reverse("place_bid", args=(auction_id,)))
 


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


class PictureWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, **kwargs):
        print(value)
        html =  Template("""
        <input type="checkbox" name="photo-clear" id="photo-clear_id">
        <label for="photo-clear_id">Clear</label>
        <br><img src="/media/$link"/> <input type="file" name="photo" accept="image/*" class="form-control-file" id="id_photo"> """)
        return mark_safe(html.substitute(link=value))

class AuctionForm(ModelForm):
    class Meta:
        model = Auction
        fields = ['name', 'category' ,'description', 'photo', 'price']

    def __init__(self, *args, **kwargs):
        super(AuctionForm, self).__init__(*args, **kwargs)
       
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            #print(self.fields[field])
            if isinstance(self.fields[field], forms.fields.ImageField):
                #self.fields[field] = forms.ImageField(widget=PictureWidget)
                self.fields[field].widget.attrs.update({'class': 'form-control-file'})
                 

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['price']

    def __init__(self, *args, **kwargs):
        super(BidForm, self).__init__(*args, **kwargs)
        self.fields['price'].label = ""
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            #print(self.fields[field])
            if isinstance(self.fields[field], forms.fields.ImageField):
                #self.fields[field] = forms.ImageField(widget=PictureWidget)
                self.fields[field].widget.attrs.update({'class': 'form-control-file'})
                      

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            #print(self.fields[field])
            if isinstance(self.fields[field], forms.fields.ImageField):
                #self.fields[field] = forms.ImageField(widget=PictureWidget)
                self.fields[field].widget.attrs.update({'class': 'form-control-file'})
                 



@login_required
def new_auction(request):
    if request.method == "POST":
        post = request.POST.copy() # to make it mutable
        print(post)
        form = AuctionForm(post, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            messages.success(request, 'Successfully created new auction! ')
        else:
            messages.error(request, 'Could not create new auction! ')
    form = AuctionForm()
    return render(request, "auctions/auction.html", {
        "form" : form
    })

@login_required
def add_comment(request):
    if request.method == "POST":
        post = request.POST.copy() # to make it mutable
        print(post)
        if not Auction.objects.filter(pk=post['auction']).exists():
            messages.error(request, 'Auction not found! ')
            return HttpResponseRedirect(reverse("index"))
        
        at = Auction.objects.get(pk=post['auction'])
        # if at.user.id == request.user.id:
        #     messages.error(request, 'Owner cannot comment on auction')
        #     return HttpResponseRedirect(reverse("place_bid", args=(post['auction'],) ))
        form = CommentForm(post)
        
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.auction = at
            form.save()
            messages.success(request, 'Successfully posted new comment! ')
        else:
            print(form.errors)
            messages.error(request, 'Could not post new comment! ')
        return HttpResponseRedirect(reverse("place_bid", args=(post['auction'],) ))
    # return render(request, "auctions/auction.html", {
    #     "form" : form
    # })

@login_required
def edit_auction(request, auction_id):
    if request.method == "POST":
        auction = Auction.objects.get(pk=auction_id, user=request.user)
        updateform = AuctionForm(request.POST, request.FILES, instance=auction)
        if updateform.is_valid():
           updateform.save()
           messages.success(request,'Changes saved! ')
           return HttpResponseRedirect(request, reverse("index"))
        else:
            messages.error(request, 'Could not save changes, please verify fields.')
        #Auction.objects.get(pk=auction_id).update(AuctionForm(request.POST))
    try:
        auction = Auction.objects.get(pk=auction_id, user=request.user)
        form = AuctionForm(instance=auction)
        return render(request, "auctions/auction.html", {
            "form" : form, 
            "edit" : True
        })
    except ObjectDoesNotExist:
        messages.error(request, 'Auction not found! ')
        return HttpResponseRedirect(reverse("new_auction") )

@login_required
def close_auction(request, auction_id):
    ac_ex = Auction.objects.filter(pk=auction_id, user=request.user).exists()
    if not ac_ex:
        messages.error(request, 'Not auction owner! ')
        return HttpResponseRedirect(reverse("index"))
    try:
        auction = Auction.objects.get(pk=auction_id, user=request.user)
        auction.active=False
        auction.save()
        messages.success(request,'Auction closed! ')
        return HttpResponseRedirect(reverse("place_bid", args=(auction_id,) ))
    except Exception as e:
        print(e)
    
   
        messages.error(request, 'Could not close auction! ')
        print(auction_id)
        return HttpResponseRedirect(request, reverse("place_bid", args=(auction_id,) ) )

@login_required
def place_bid(request, auction_id):
    
    exists = Auction.objects.filter(pk=auction_id).exists()
    if not exists:
        messages.error(request, 'Auction not found!')
        return HttpResponseRedirect(reverse("index") )
    auction = Auction.objects.get(pk=auction_id)
    active = auction.active
    if request.method == "POST" and active and exists:
        
            
        form = BidForm(request.POST)
        if form.is_valid() and request.user.id!=auction.user.id:
            bid_price =0
            bid = Bid.objects.filter(auction=auction).latest('price') if Bid.objects.filter(auction=auction).exists() else None   
            if bid:
                bid_price = bid.price
            if int(form.cleaned_data['price']) > int(auction.price) and int(form.cleaned_data['price']) > int(bid_price): 
                form = form.save(commit=False)
                form.auction = auction
                form.user = request.user
                form.save()
                messages.success(request,'Bid Placed! ')
            else: 
                messages.error(request,'Could not place bid! ')
        else:
            messages.error(request,'Could not place bid! ')
    # try:
    auction = Auction.objects.get(pk=auction_id)
    bid = Bid.objects.filter(auction=auction).latest('price') if Bid.objects.filter(auction=auction).exists() else None     
    
    
    if bid:
        auction.current_bid = bid.price
        n_bid = Bid.objects.filter(auction=auction).count()
        auction.number_bid = n_bid
        auction.save()
        form = BidForm(instance=bid)
    else: 
        form = BidForm()
    comment = Comment.objects.filter(auction=auction)
    auction.in_watchlist=in_watchlist(request.user.id, auction.id)    
    return render (request, "auctions/list.html", {
            "form" : form, 
            "auction" : auction,
            "bid" : bid,
            "comment": comment,
            "user": request.user
    })
    # except Exception as e:
    #     print(e)
    #     return HttpResponseRedirect(reverse("index"))