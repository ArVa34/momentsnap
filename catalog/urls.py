from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("shop/", views.item_list, name="item_list"),
    path("shop/<slug:category_slug>/", views.item_list, name="category_items"),
    path("item/<slug:slug>/", views.item_detail, name="item_detail"),
    path("item/<int:item_id>/rate/", views.rate_item, name="rate_item"),
]