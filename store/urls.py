from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),   # homepage
    path("store/", views.store_page, name="store_page"),
    # Checkout flows
    path("checkout/", views.checkout, name="checkout"),                # cart checkout
    path("checkout/<int:product_id>/", views.checkout_product, name="checkout_product"),  # single product checkout
    path("buy_now/<int:product_id>/", views.buy_now, name="buy_now"),  # Buy Now button

    # Payment flow
    path("upi_page/<int:order_id>/", views.upi_page, name="upi_page"),
    path("check-scan/<int:order_id>/", views.check_scan, name="check_scan"),
    path("payment_success/<int:order_id>/", views.payment_success, name="payment_success"),
   path(
    'upi_qr/<int:amount>/<int:order_id>/',
    views.upi_qr,
    name='upi_qr'
),
    path(
    "scan-success/<int:order_id>/",
    views.scan_success,
    name="scan_success"
),
    # Orders
    path("orders/", views.orders, name="orders"),

    # Cart
    path("cart/", views.cart, name="cart"),
    path("add_to_cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("remove_from_cart/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("increase_quantity/<int:item_id>/", views.increase_quantity, name="increase_quantity"),
    path("decrease_quantity/<int:item_id>/", views.decrease_quantity, name="decrease_quantity"),
    path("clear_cart/", views.clear_cart, name="clear_cart"),
    path('invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    # Product detail
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),

    # Success page
    path("success/", views.success, name="success"),
   path('track-order/<int:order_id>/', views.track_order, name='track_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
# urls.py
path('iphone/', views.iphone_page, name='iphone_page'),
path(
    'category/<str:category>/',
    views.category_page,
    name='category'
)

]
