from io import BytesIO
from reportlab.pdfgen import canvas
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
import qrcode
from reportlab.lib.utils import ImageReader
import os
from .models import Product, Cart, CartItem, Order, OrderItem


def home(request):

    query = request.GET.get('q', '')

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )
    else:
        products = Product.objects.all()

    return render(request, 'home.html', {
        'products': products,
        'query': query
    })

def checkout(request):
    cart_id = request.session.get("cart_id")

    cart = Cart.objects.first()

    if cart:
        items = CartItem.objects.filter(cart=cart)
    else:
        items = []
    if not items.exists():
        return render(request, "checkout.html", {
            "error": "Your cart is empty"
        })

    total = sum(item.product.price * item.quantity for item in items)

    if request.method == "POST":

        customer_name = request.POST.get("customer_name")
        phone = request.POST.get("phone")
        
        address = request.POST.get('address')
        print("ADDRESS:", address)

    if not address:
        return HttpResponse("Address is required")
        payment_method = request.POST.get("payment_method")

        # 1. Create Order
        order = Order.objects.create(
    customer_name=customer_name,
    phone=phone,
    payment_method=payment_method,
    total=total,
    status="Pending"
)

        # 2. Create Order Items
        for item in items:
           OrderItem.objects.create(
            order=order,
             product=product.name,
            quantity=1,
             price=product.price
            )

        # 3. Clear cart
        items.delete()

        return redirect("order_success")

    return render(request, "checkout.html", {
        "items": items,
        "total": total
    })
def checkout_product(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":

        customer_name = request.POST.get("customer_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        
        address = request.POST.get("address", "").strip()
        payment_method = request.POST.get("payment_method", "").strip()
        order = Order.objects.create(
            customer_name=customer_name,
            phone=phone,
            payment_method=payment_method,
            total=product.price,
             address=address,
            status="Pending"
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
             price=product.price
)

        if payment_method == "UPI":
            return redirect("upi_page", order_id=order.id)

        if payment_method == "COD":
            order.status = "Paid"
            order.save()
            return redirect("payment_success", order_id=order.id)

        return redirect("payment_success", order_id=order.id)

    # GET request
    return render(
        request,
        "checkout.html",
        {
            "product": product,
            "total": product.price,
        }
    )
def buy_now(request, product_id):
    return redirect("checkout_product", product_id=product_id)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "product_detail.html", {"product": product})


# CART
def cart(request):
    cart_id = request.session.get("cart_id")
    items = Cart.objects.filter(cart_id=cart_id)

    total = sum(item.product.price * item.quantity for item in items)

    return render(request, "cart.html", {
        "items": items,
        "total": total
    })

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart, created = Cart.objects.get_or_create(id=1)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1

    cart_item.save()

    return redirect("cart")


def increase_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    item.quantity += 1
    item.save()

    return redirect("cart")


def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect("cart")


def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()

    return redirect("cart")


def clear_cart(request):
    CartItem.objects.filter(cart_id=1).delete()
    return redirect("cart")


# ORDERS
def orders(request):
    all_orders = Order.objects.all().order_by("-id")

    return render(request, "orders.html", {
        "orders": all_orders
    })


# PAYMENT
def upi_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    product = order.items.first()

    return render(
        request,
        "payment.html",
        {
            "order": order,
            "product": product,
            "amount": order.total,
        }
    )


def check_scan(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    return JsonResponse({
        "scanned": order.scanned
    })
def payment_success(request, order_id):

    order = Order.objects.get(id=order_id)

    order.status = "Paid"
    order.save()

    for item in order.items.all():
        try:
            product = Product.objects.get(name=item.product)

            if product.stock >= item.quantity:
                product.stock -= item.quantity
                product.save()

        except Product.DoesNotExist:
            pass

    return render(
        request,
        "success.html",
        {
            "order": order
        }
    )
def upi_qr(request, amount, order_id):
    url = f"http://10.15.125.152:8000/scan-success/{order_id}"
    print("QR URL:", url)

    qr = qrcode.make(url)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    return HttpResponse(
        buffer.getvalue(),
        content_type="image/png"
    )
def scan_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    order.scanned = True
    order.save()

    return render(request, "payment_processing.html", {
        "order": order
    })
def category_products(request, category):
    products = Product.objects.filter(
        category__iexact=category
    )

    return render(
        request,
        'store/category.html',
        {
            'products': products,
            'category': category
        }
    )
    # views.py
def iphone_page(request):
    products = Product.objects.filter(category="iPhone")
    return render(request, "store/iphone.html", {
        "products": products
    })
def mac_page(request):
    products = Product.objects.filter(category__icontains='mac')
    return render(request,'store/mac.html',{'products':products})

def ipad_page(request):
    products = Product.objects.filter(category__icontains='ipad')
    return render(request,'store/ipad.html',{'products':products})

def watch_page(request):
    products = Product.objects.filter(category__icontains='watch')
    return render(request,'store/watch.html',{'products':products})

def airpods_page(request):
    products = Product.objects.filter(category__icontains='airpods')
    return render(request,'store/airpods.html',{'products':products})

def vision_page(request):
    products = Product.objects.filter(category__icontains='vision')
    return render(request,'store/vision.html',{'products':products})

def store_page(request):
    products = Product.objects.all()
    return render(request,'store/store_page.html',{'products':products})

def category_page(request, category):

    category_key = category.lower()

    products = Product.objects.filter(
        category__iexact=category
    )

    hero_images = {
        "iphone": "images/iphone.png",
        "mac": "images/mac.png",
        "ipad": "images/ipad.png",
        "watch": "images/watch.png",
        "airpods": "images/airpods.png",
        "tvhome": "images/vision.png",
        "accessories": "images/access.png",
        
     }

    return render(request, "store/category.html", {
        "products": products,
        "category": category,
        "hero_image": hero_images.get(category_key)
    })
def store_page(request):
    products = Product.objects.all()

    return render(request, "store/store_page.html", {
        "products": products
    })
def success(request):
    return render(request, "success.html")
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    return render(request, "track_order.html", {
        "order": order
    })

from .models import Order

def my_orders(request):
    orders = Order.objects.all().order_by('-created_at')

    return render(request, 'my_orders.html', {
        'orders': orders
    })
def download_invoice(request, order_id):
    order = Order.objects.get(id=order_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="INV-{order.id}.pdf"'
    )

    p = canvas.Canvas(response)

    # ===== STORE LOGO =====
    logo_path = os.path.join(
        'media',
        'logo.png'      # change to your logo filename
    )

    if os.path.exists(logo_path):
        p.drawImage(
            ImageReader(logo_path),
            50, 760,
            width=80,
            height=80
        )
    if order.product and order.product.image:
        product_image = order.product.image.path

    if os.path.exists(product_image):
        p.drawImage(
            ImageReader(product_image),
            350, 550,
            width=150,
            height=150,
            preserveAspectRatio=True
        )
    # ===== STORE NAME =====
    p.setFont("Helvetica-Bold", 20)
    p.drawString(150, 800, "iMart")
    p.line(50, 750, 550, 750)
    # ===== INVOICE NUMBER =====
    invoice_no = f"INV-{order.created_at.year}-{order.id:05d}"

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 720, f"Invoice Number: {invoice_no}")

    # ===== ORDER DATE =====
    p.setFont("Helvetica", 12)
    p.drawString(
        50,
        700,
        f"Order Date: {order.created_at.strftime('%d %B %Y')}"
    )

    # ===== CUSTOMER DETAILS =====
    p.drawString(50, 660, f"Customer: {order.customer_name}")
    p.drawString(50, 640, f"Phone: {order.phone}")
    p.drawString(50, 620, f"Address: {order.address}")

    # ===== PRODUCT =====
    if order.product:
        p.drawString(
            50,
            580,
            f"Product: {order.product.name}"
        )

    # ===== ORDER DETAILS =====
    p.drawString(
        50,
        540,
        f"Payment Method: {order.payment_method}"
    )

    p.drawString(
        50,
        520,
        f"Order Status: {order.status}"
    )

    p.setFont("Helvetica-Bold", 14)
    p.drawString(
        50,
        480,
        f"Total Amount: ₹{order.total}"
    )

    p.drawString(
        50,
        430,
        "iMart | Thank you for your purchase"
)
    

    p.save()
    return response
    