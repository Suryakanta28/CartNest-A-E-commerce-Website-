from decimal import Decimal
from django.conf import settings
from .models import Product


class Cart:
    """Session-backed shopping cart with validation against database stock."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        Validates against current product stock and active state.
        Returns a tuple: (success: bool, message: str)
        """
        if not product.is_active:
            return False, "This product is currently unavailable."

        if product.stock <= 0:
            return False, f"Sorry, '{product.name}' is out of stock."

        product_id = str(product.id)

        current_qty = 0
        if product_id in self.cart and not override_quantity:
            current_qty = self.cart[product_id]['quantity']

        new_qty = quantity if override_quantity else current_qty + quantity

        if new_qty > product.stock:
            # Cannot add more than available stock
            if product_id not in self.cart:
                # Add up to available stock if possible
                self.cart[product_id] = {
                    'quantity': product.stock,
                    'price': str(product.price),
                }
                self.save()
                return True, f"Only {product.stock} units available for '{product.name}'. Added {product.stock} to cart."
            return False, f"Cannot add {quantity} more. Only {product.stock} total in stock (you already have {current_qty} in cart)."

        if new_qty <= 0:
            self.remove(product)
            return True, f"Removed '{product.name}' from your cart."

        # Always update price from the database record snapshot
        self.cart[product_id] = {
            'quantity': new_qty,
            'price': str(product.price),
        }
        self.save()
        return True, f"Added '{product.name}' to your cart."

    def update_quantity(self, product, quantity):
        """Update the quantity of a product in the cart directly."""
        return self.add(product, quantity=quantity, override_quantity=True)

    def remove(self, product):
        """Remove a product from the cart."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def remove_by_id(self, product_id):
        """Remove a product by ID string."""
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        """Mark the session as modified to ensure it gets saved."""
        self.session.modified = True

    def __iter__(self):
        """
        Iterate over the items in the cart and retrieve active products from the database.
        Automatically purges items whose products no longer exist or are inactive.
        """
        product_ids = list(self.cart.keys())
        products = Product.objects.filter(id__in=product_ids, is_active=True)
        products_map = {str(p.id): p for p in products}

        # Find any stale product IDs that are no longer active or in database
        stale_ids = [pid for pid in product_ids if pid not in products_map]
        if stale_ids:
            for stale_id in stale_ids:
                del self.cart[stale_id]
            self.save()

        # Copy cart data to prevent modifying the raw session during iteration
        for product_id, item in list(self.cart.items()):
            product = products_map.get(product_id)
            if not product:
                continue

            # Recalculate price from DB product record
            unit_price = product.price
            quantity = item['quantity']

            item_data = {
                'product_id': product_id,
                'product': product,
                'price': unit_price,
                'quantity': quantity,
                'total_price': unit_price * quantity,
            }
            yield item_data

    def __len__(self):
        """Count all items in the cart (sum of quantities)."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Calculate total price of all items in the cart."""
        return sum(item['total_price'] for item in self)

    def is_empty(self):
        """Check whether the cart is empty."""
        return len(self.cart) == 0

    def clear(self):
        """Clear all items from the session cart."""
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.save()
