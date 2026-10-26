from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse

from .models import Category, Product, ProductImage, Order, OrderItem
from .forms import (
    UserRegisterForm,
    UserLoginForm,
    UserProfileForm,
    AddToCartForm,
    CheckoutForm,
    ProductForm,
)
from .cart import Cart


def home(request):
    """Store home page with hero section, featured categories, and latest products."""
    categories = Category.objects.annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    ).filter(product_count__gt=0)[:6]

    # Select flagship product for the hero banner
    hero_product = Product.objects.filter(is_active=True, slug='aura-studio-wireless-anc-headphones').first()
    if not hero_product:
        hero_product = Product.objects.filter(is_active=True).first()

    featured_products = Product.objects.filter(is_active=True).select_related('category')[:8]
    latest_products = Product.objects.filter(is_active=True).select_related('category').order_by('-created_at')[:4]

    context = {
        'hero_product': hero_product,
        'categories': categories,
        'featured_products': featured_products,
        'latest_products': latest_products,
    }
    return render(request, 'store/home.html', context)


def product_list(request, category_slug=None):
    """
    Product listing page with category filtering, search queries,
    sorting, and pagination.
    """
    category = None
    categories = Category.objects.annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    )

    products = Product.objects.filter(is_active=True).select_related('category')

    # Category filter
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Search filter
    search_query = request.GET.get('q', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price-asc':
        products = products.order_by('price')
    elif sort == 'price-desc':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    else:  # newest
        products = products.order_by('-created_at')

    # Pagination: 9 products per page
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    context = {
        'category': category,
        'categories': categories,
        'products': page_obj,
        'search_query': search_query,
        'sort': sort,
        'total_count': Product.objects.filter(is_active=True).count(),
        'results_count': products.count(),
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    """Product detail page with stock status, description, add-on bundle pack, and expanded recommendations."""
    product = get_object_or_404(Product.objects.select_related('category'), slug=slug, is_active=True)
    form = AddToCartForm()

    # 1. Frequently Bought Together / Add-on Products
    # Pick 2 complementary in-stock items
    addon_pool = Product.objects.filter(is_active=True, stock__gt=0).exclude(id=product.id)
    same_cat_addons = list(addon_pool.filter(category=product.category).order_by('price')[:2])
    other_cat_addons = list(addon_pool.exclude(category=product.category).order_by('price')[:2])

    addon_products = []
    if same_cat_addons:
        addon_products.append(same_cat_addons[0])
    if other_cat_addons:
        addon_products.append(other_cat_addons[0])
    if len(addon_products) < 2 and len(same_cat_addons) > 1:
        addon_products.append(same_cat_addons[1])
    elif len(addon_products) < 2 and len(other_cat_addons) > 1:
        addon_products.append(other_cat_addons[1])

    # Initial bundle total: main product + all suggested add-ons
    bundle_total = product.price + sum(p.price for p in addon_products)
    addon_ids = [p.id for p in addon_products]

    # 2. Related Products from same category (excluding current item & add-ons)
    related_products = list(Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).exclude(id__in=addon_ids)[:4])

    # If fewer than 4 related products in same category, backfill from other categories
    if len(related_products) < 4:
        needed = 4 - len(related_products)
        excluded_ids = [product.id] + addon_ids + [p.id for p in related_products]
        backfill = list(Product.objects.filter(
            is_active=True
        ).exclude(id__in=excluded_ids).order_by('-created_at')[:needed])
        related_products.extend(backfill)

    # 3. Trending Gear / Customers Also Bought (More to explore)
    used_ids = [product.id] + addon_ids + [p.id for p in related_products]
    recommended_products = list(Product.objects.filter(
        is_active=True
    ).exclude(id__in=used_ids).order_by('-created_at')[:4])

    context = {
        'product': product,
        'form': form,
        'addon_products': addon_products,
        'bundle_total': bundle_total,
        'related_products': related_products,
        'recommended_products': recommended_products,
    }
    return render(request, 'store/product_detail.html', context)


def product_add_image(request, slug):
    """Allow uploading or adding new gallery angles/photos to a specific product directly."""
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        image_file = request.FILES.get('image')
        alt_text = request.POST.get('alt_text', '').strip()
        set_as_main = request.POST.get('set_as_main') == 'on'

        if image_file:
            if set_as_main:
                product.image = image_file
                product.save()
                messages.success(request, f"Updated main photo for '{product.name}'!")
            else:
                next_order = product.gallery_images.count() + 1
                ProductImage.objects.create(
                    product=product,
                    image=image_file,
                    alt_text=alt_text or f"{product.name} - View {next_order}",
                    order=next_order
                )
                messages.success(request, f"Added new angle image to '{product.name}' gallery!")
        else:
            messages.warning(request, "Please choose an image file to upload.")

    return redirect('store:product_detail', slug=product.slug)


def cart_view(request):
    """Shopping cart page displaying items, quantities, and totals."""
    cart = Cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


def cart_add(request, product_id):
    """Add a product to the cart with the requested quantity."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = Cart(request)

    quantity = 1
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
        else:
            try:
                quantity = int(request.POST.get('quantity', 1))
            except (ValueError, TypeError):
                quantity = 1

    success, message_text = cart.add(product, quantity=quantity)

    # Return JSON for AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
        return JsonResponse({
            'success': success,
            'message': message_text,
            'cart_total_items': len(cart),
            'cart_total_price': str(cart.get_total_price()),
        })

    if success:
        messages.success(request, message_text)
    else:
        messages.error(request, message_text)

    # Redirect to cart or referrer
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('store:cart')


def cart_add_bundle(request):
    """Add multiple selected products (bundle / add-on items) to cart at once."""
    if request.method == 'POST':
        cart = Cart(request)
        product_ids = request.POST.getlist('product_ids')
        added_count = 0
        added_names = []
        for pid in product_ids:
            try:
                prod = Product.objects.filter(id=pid, is_active=True).first()
                if prod and prod.stock > 0:
                    qty_param = request.POST.get(f'quantity_{pid}', 1)
                    qty = int(qty_param) if qty_param else 1
                    success, msg = cart.add(prod, quantity=max(1, qty))
                    if success:
                        added_count += 1
                        added_names.append(prod.name)
            except (ValueError, TypeError):
                continue

        if added_count > 0:
            messages.success(request, f"Bundle added! {added_count} items added to your cart.")
        else:
            messages.warning(request, "No items could be added to your cart.")

        # Return JSON for AJAX requests
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({
                'success': added_count > 0,
                'added_count': added_count,
                'cart_total_items': len(cart),
                'cart_total_price': str(cart.get_total_price()),
            })

        next_url = request.POST.get('next')
        if next_url:
            return redirect(next_url)
    return redirect('store:cart')


def cart_update(request, product_id):
    """Update quantity of an item in the cart."""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = Cart(request)
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

        if quantity <= 0:
            cart.remove(product)
            messages.info(request, f"Removed '{product.name}' from your cart.")
        else:
            success, message_text = cart.update_quantity(product, quantity)
            if success:
                messages.success(request, message_text)
            else:
                messages.warning(request, message_text)

    return redirect('store:cart')


def cart_remove(request, product_id):
    """Remove a product from the cart."""
    if request.method == 'POST':
        cart = Cart(request)
        cart.remove_by_id(product_id)
        messages.info(request, "Item removed from your cart.")
    return redirect('store:cart')


def register_view(request):
    """Register a new user account."""
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to CartNest, {user.first_name or user.username}! Your account has been created.")
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('store:home')
    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """Log in an existing user."""
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('store:home')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    """Log out the current user."""
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('store:home')


@login_required
def profile_view(request):
    """User profile page allowing name/email updates and showing recent orders."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been updated successfully.")
            return redirect('store:profile')
    else:
        form = UserProfileForm(instance=request.user)

    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    total_orders = Order.objects.filter(user=request.user).count()

    context = {
        'form': form,
        'recent_orders': recent_orders,
        'total_orders': total_orders,
    }
    return render(request, 'store/profile.html', context)


@login_required
def checkout_view(request):
    """
    Checkout page. Validates server-side stock availability,
    creates Order and OrderItems in an atomic transaction,
    reduces stock, clears the cart, and redirects to confirmation.
    """
    cart = Cart(request)

    # 1. Prevent checkout with empty cart
    if cart.is_empty() or len(cart) == 0:
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('store:cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # 2. Server-side atomic transaction for stock validation and order creation
            try:
                with transaction.atomic():
                    # Collect and validate each product with row locking
                    order_items_to_create = []
                    total_amount = Decimal('0.00')

                    for item in cart:
                        # Re-fetch product record from DB inside transaction
                        try:
                            product = Product.objects.select_for_update().get(
                                id=item['product_id'],
                                is_active=True
                            )
                        except Product.DoesNotExist:
                            raise ValueError(f"Product '{item.get('product')}' is no longer available.")

                        requested_qty = item['quantity']
                        if requested_qty <= 0:
                            raise ValueError(f"Invalid quantity for '{product.name}'.")

                        # Validate stock availability
                        if product.stock < requested_qty:
                            raise ValueError(
                                f"Insufficient stock for '{product.name}'. "
                                f"Requested {requested_qty}, but only {product.stock} available."
                            )

                        # Recalculate price from DB record snapshot (never client input!)
                        unit_price = product.price
                        subtotal = unit_price * requested_qty
                        total_amount += subtotal

                        # Prepare item snapshot & reduce product stock
                        product.stock -= requested_qty
                        product.save()

                        order_items_to_create.append({
                            'product': product,
                            'product_name': product.name,
                            'price': unit_price,
                            'quantity': requested_qty,
                            'subtotal': subtotal,
                        })

                    # Create Order record
                    order = Order.objects.create(
                        user=request.user,
                        full_name=form.cleaned_data['full_name'],
                        phone_number=form.cleaned_data['phone_number'],
                        address_line1=form.cleaned_data['address_line1'],
                        city=form.cleaned_data['city'],
                        postal_code=form.cleaned_data['postal_code'],
                        total_amount=total_amount,
                        payment_method=form.cleaned_data['payment_method'],
                        status=Order.STATUS_PENDING,
                    )

                    # Create OrderItem records snapshot
                    for item_data in order_items_to_create:
                        OrderItem.objects.create(
                            order=order,
                            product=item_data['product'],
                            product_name=item_data['product_name'],
                            price=item_data['price'],
                            quantity=item_data['quantity'],
                            subtotal=item_data['subtotal'],
                        )

                    # Clear cart after successful order
                    cart.clear()

                    messages.success(request, f"Order #{order.order_number} has been placed successfully!")
                    return redirect('store:order_confirmation', order_number=order.order_number)

            except ValueError as e:
                # Transaction will be rolled back automatically
                messages.error(request, str(e))
                return redirect('store:cart')
            except Exception as e:
                messages.error(request, "An unexpected error occurred while processing your order. Please try again.")
                return redirect('store:cart')
    else:
        # Pre-fill full name with user's stored first/last name
        initial_name = f"{request.user.first_name} {request.user.last_name}".strip()
        form = CheckoutForm(initial={'full_name': initial_name})

    context = {
        'form': form,
        'cart': cart,
    }
    return render(request, 'store/checkout.html', context)


@login_required
def order_confirmation(request, order_number):
    """
    Order confirmation page with receipt details.
    Enforces strict user ownership verification.
    """
    order = get_object_or_404(
        Order.objects.prefetch_related('items'),
        order_number=order_number,
        user=request.user
    )
    return render(request, 'store/order_confirmation.html', {'order': order})


@login_required
def my_orders(request):
    """
    User's order history page.
    Enforces that users can view only their own orders.
    """
    orders_list = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')

    paginator = Paginator(orders_list, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/my_orders.html', {'orders': page_obj})


@login_required
def order_detail(request, order_number):
    """
    Detailed view of a single order.
    Enforces strict user ownership verification (404 if not the owner).
    """
    order = get_object_or_404(
        Order.objects.prefetch_related('items'),
        order_number=order_number,
        user=request.user
    )
    return render(request, 'store/order_detail.html', {'order': order})


@login_required
def add_product(request):
    """
    Staff-only portal to add new products directly from the web interface.
    Validates form data, handles image upload to media/products/,
    and publishes the new product to the storefront.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access denied. Only staff members and administrators can add new products.")
        return redirect('store:home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(
                request,
                f"Product '{product.name}' was successfully created and is now live on the store!"
            )
            return redirect('store:product_detail', slug=product.slug)
        else:
            messages.error(request, "Please review the errors highlighted below and try again.")
    else:
        form = ProductForm()

    return render(request, 'store/add_product.html', {'form': form})


def custom_404_view(request, exception=None):
    """Custom 404 error page."""
    return render(request, 'errors/404.html', status=404)

