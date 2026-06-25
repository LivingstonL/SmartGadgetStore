from .models import Product

CART_SESSION_ID = "cart"


def get_cart(session):
    return session.get(CART_SESSION_ID, {})


def save_cart(session, cart):
    session[CART_SESSION_ID] = cart
    session.modified = True


def add_to_cart(session, product_id):
    cart = get_cart(session)
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    save_cart(session, cart)


def remove_from_cart(session, product_id):
    cart = get_cart(session)
    cart.pop(str(product_id), None)
    save_cart(session, cart)


def clear_cart(session):
    save_cart(session, {})


def cart_items(session):
    cart = get_cart(session)

    items = []
    total = 0

    for pid, qty in cart.items():
        product = Product.objects.get(id=pid)
        subtotal = product.price * qty

        items.append({
            "product": product,
            "qty": qty,
            "subtotal": subtotal
        })

        total += subtotal

    return items, total