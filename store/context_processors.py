from .cart import Cart
from .models import Category


def cart_context(request):
    """
    Context processor to provide cart information and categories
    to all templates globally.
    """
    cart = Cart(request)
    return {
        'cart': cart,
        'cart_total_items': len(cart),
        'cart_total_price': cart.get_total_price(),
        'header_categories': Category.objects.all()[:8],
    }
