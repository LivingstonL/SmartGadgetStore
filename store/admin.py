from django.contrib import admin
from .models import Product, Cart, CartItem, Order, OrderItem, PaymentScan


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock")
    search_fields = ("name", "category")


admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
admin.site.register(PaymentScan)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "product_name",
        "customer_name",
        "phone",
        "address",
        "payment_method",
        "total",
        "payment_status",
        'tracking_number',
        'status_badge',
        "created_at",
    )

    list_filter = (
        "payment_status",
    )
    actions = ['mark_as_shipped', 'mark_as_delivered']


    @admin.action(description="Mark selected orders as Shipped")
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='Shipped')

    search_fields = (
    'customer_name',
    'phone',
    'tracking_number'
)
    list_filter = (
    'status',
    'delivery_status',

)
    @admin.action(description="Mark selected orders as Delivered")
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='Delivered')
    search_fields = (
        "customer_name",
        "phone",
        "tracking_number",
    )
    actions = [
    'mark_as_shipped',
    'mark_as_delivered',
    'mark_as_cancelled'
]
    @admin.action(description="Cancel selected orders")
    def mark_as_cancelled(self, request, queryset):
     queryset.update(status='Cancelled')

    def product_name(self, obj):
     if obj.product and hasattr(obj.product, "name"):
        return obj.product.name
     return "No Product"
    
    def status_badge(self, obj):
        if obj.status == "Pending":
            return "🟡 Pending"
        elif obj.status == "Shipped":
         return "🚚 Shipped"
        elif obj.status == "Delivered":
            return "✅ Delivered"
        return obj.status

    status_badge.short_description = "Delivery Status"
    def payment_status(self, obj):
     return obj.status

    payment_status.short_description = "Payment"