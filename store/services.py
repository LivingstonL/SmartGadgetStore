from .models import Order, OrderItem


def create_order(user_data, items, total):
    order = Order.objects.create(
        fullname=user_data["fullname"],
        phone=user_data["phone"],
        address=user_data["address"],
        landmark=user_data.get("landmark", ""),
        payment_method=user_data["payment_method"],
        total=total
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            quantity=item["qty"],
            price=item["product"].price
        )

    return order