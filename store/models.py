from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
# ==========================
# PRODUCTS
# ==========================
class Product(models.Model):

    CATEGORY_CHOICES = [
        ("iPhone", "iPhone"),
        ("iPad", "iPad"),
        ("Mac", "Mac"),
        ("Watch", "Watch"),
        ("AirPods", "AirPods"),
        ("Accessories", "Accessories"),
        ("Vision", "Vision"),
    ]

    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='products/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to="products/")
    hero_image = models.ImageField(
        upload_to="hero_images/",
        blank=True,
        null=True
    )

    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


# ==========================
# CART
# ==========================
class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.product.name

# ==========================
# ORDER
# ==========================
class Order(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    PAYMENT_CHOICES = [
        ('UPI', 'UPI'),
        ('COD', 'Cash on Delivery'),
    ]
    customer_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(null=False, blank=False)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(
    max_length=20,
    choices=PAYMENT_CHOICES,
    blank=True
)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="Pending")
    scanned = models.BooleanField(default=False)

    tracking_number = models.CharField(
    max_length=20,
    unique=True,
    blank=True
)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)   # Save first to get ID

        if not self.tracking_number:
            self.tracking_number = f"SGS{100000 + self.id}"
            super().save(update_fields=['tracking_number'])

    delivery_status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.customer_name

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.CharField(max_length=200)

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.product
    # ORDER ITEMS
# ==========================

# ==========================
# PAYMENT SCAN
# ==========================
class PaymentScan(models.Model):

    order_id = models.IntegerField()

    scanned = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.order_id}"
# ==========================
# DELIVERY
# ==========================
class Delivery(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='delivery'
    )

    tracking_number = models.CharField(max_length=50, blank=True)

    DELIVERY_STATUS = [
        ('Processing', 'Processing'),
        ('Packed', 'Packed'),
        ('Shipped', 'Shipped'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
    ]

    delivery_status = models.CharField(
        max_length=30,
        choices=DELIVERY_STATUS,
        default='Processing'
    )