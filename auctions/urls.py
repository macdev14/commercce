from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("category/<int:category_id>", views.category, name="category"),
    path("category/", views.all_category, name="all-category"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/add/<int:auction_id>", views.watchlist_add, name="watchlist_add"),
    path("watchlist/delete/<int:auction_id>", views.watchlist_delete, name="watchlist_delete"),
    path("new", views.new_auction, name="new_auction"),
    path("edit/<int:auction_id>", views.edit_auction, name="edit_auction"),
    path("bid/<int:auction_id>", views.place_bid, name="place_bid"),
    path("comment/", views.add_comment, name="add_comment"),
    path("close/<int:auction_id>", views.close_auction, name="close_auction"),
    path("winner/", views.winning, name="winner")
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
