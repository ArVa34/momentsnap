from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ["item", "item_name", "unit_price", "quantity"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "status", "total", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["full_name", "email", "payment_reference"]
    readonly_fields = ["user", "total", "payment_reference", "created_at"]
    inlines = [OrderItemInline]