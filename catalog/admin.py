from django.contrib import admin

from .models import Category, Item, ItemView, Rating, SearchQuery  



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "slug"]
    list_filter = ["parent"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "stock", "event_type", "is_active"]
    list_filter = ["is_active", "is_event_package", "event_type", "style", "category"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ["term", "results_count", "user", "searched_at"]
    list_filter = ["searched_at"]
    search_fields = ["term"]


@admin.register(ItemView)
class ItemViewAdmin(admin.ModelAdmin):
    list_display = ["item", "user", "viewed_at"]
    list_filter = ["viewed_at"]


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ["item", "user", "stars", "updated_at"]
    list_filter = ["stars", "updated_at"]
    search_fields = ["item__name", "user__username", "review"]