from django.contrib import admin

from .models import Category, Item, SearchQuery



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "slug"]
    list_filter = ["parent"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "stock", "event_type", "is_active"]
    list_filter = ["is_active", "event_type", "style", "category"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ["name"]}

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ["term", "results_count", "user", "searched_at"]
    list_filter = ["searched_at"]
    search_fields = ["term"]