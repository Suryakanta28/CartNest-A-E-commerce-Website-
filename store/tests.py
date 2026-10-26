from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Product, Order, OrderItem
from .cart import Cart


class AuthenticationTests(TestCase):
    """Test user registration, login, logout, and profile management."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )

    def test_user_registration_success(self):
        response = self.client.post(reverse('store:register'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'Customer',
            'email': 'newuser@example.com',
            'password1': 'strongpass123',
            'password2': 'strongpass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        new_user = User.objects.get(username='newuser')
        self.assertTrue(new_user.check_password('strongpass123'))

    def test_user_registration_duplicate_email(self):
        response = self.client.post(reverse('store:register'), {
            'username': 'anotheruser',
            'first_name': 'Another',
            'last_name': 'User',
            'email': 'testuser@example.com',  # already exists
            'password1': 'strongpass123',
            'password2': 'strongpass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='anotheruser').exists())

    def test_user_login_success(self):
        response = self.client.post(reverse('store:login'), {
            'username': 'testuser',
            'password': 'testpassword123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_user_login_invalid_credentials(self):
        response = self.client.post(reverse('store:login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_user_logout(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('store:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_profile_update(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.post(reverse('store:profile'), {
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast',
            'email': 'updated@example.com',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'UpdatedFirst')
        self.assertEqual(self.user.email, 'updated@example.com')


class ProductCatalogTests(TestCase):
    """Test product browsing, category filtering, search, and visibility."""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Audio', slug='audio')
        self.product_active = Product.objects.create(
            category=self.category,
            name='Noise Cancelling Headphones',
            slug='nc-headphones',
            description='Crisp highs and deep bass.',
            price=Decimal('150.00'),
            stock=10,
            is_active=True
        )
        self.product_inactive = Product.objects.create(
            category=self.category,
            name='Discontinued Earbuds',
            slug='discontinued-earbuds',
            description='Legacy product.',
            price=Decimal('50.00'),
            stock=5,
            is_active=False
        )

    def test_home_page_status(self):
        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Noise Cancelling Headphones')
        self.assertNotContains(response, 'Discontinued Earbuds')

    def test_product_list_active_only(self):
        response = self.client.get(reverse('store:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Noise Cancelling Headphones')
        self.assertNotContains(response, 'Discontinued Earbuds')

    def test_category_filtering(self):
        response = self.client.get(reverse('store:product_list_by_category', kwargs={'category_slug': 'audio'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Noise Cancelling Headphones')

    def test_product_search(self):
        response = self.client.get(reverse('store:product_list') + '?q=Cancelling')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Noise Cancelling Headphones')

        # Non-matching search
        response_empty = self.client.get(reverse('store:product_list') + '?q=NonExistentItemXYZ')
        self.assertEqual(response_empty.status_code, 200)
        self.assertContains(response_empty, 'No products found')

    def test_product_detail_page(self):
        # Active product returns 200
        response = self.client.get(reverse('store:product_detail', kwargs={'slug': 'nc-headphones'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Noise Cancelling Headphones')

        # Inactive product returns 404
        response_inactive = self.client.get(reverse('store:product_detail', kwargs={'slug': 'discontinued-earbuds'}))
        self.assertEqual(response_inactive.status_code, 404)


class ShoppingCartTests(TestCase):
    """Test cart additions, updates, removals, and stock checks."""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Tech', slug='tech')
        self.product = Product.objects.create(
            category=self.category,
            name='Mechanical Keyboard',
            slug='mechanical-keyboard',
            description='Smooth typing.',
            price=Decimal('100.00'),
            stock=5,
            is_active=True
        )
        self.out_of_stock_product = Product.objects.create(
            category=self.category,
            name='Sold Out Mouse',
            slug='sold-out-mouse',
            description='Out of stock.',
            price=Decimal('30.00'),
            stock=0,
            is_active=True
        )

    def test_add_to_cart_and_view(self):
        response = self.client.post(reverse('store:cart_add', kwargs={'product_id': self.product.id}), {
            'quantity': 2
        })
        self.assertEqual(response.status_code, 302)

        # Inspect cart page
        cart_page = self.client.get(reverse('store:cart'))
        self.assertEqual(cart_page.status_code, 200)
        self.assertContains(cart_page, 'Mechanical Keyboard')
        self.assertContains(cart_page, '200.00')

    def test_update_cart_quantity(self):
        # Add 1 item
        self.client.post(reverse('store:cart_add', kwargs={'product_id': self.product.id}), {'quantity': 1})
        # Update to 4 items
        self.client.post(reverse('store:cart_update', kwargs={'product_id': self.product.id}), {'quantity': 4})

        cart_page = self.client.get(reverse('store:cart'))
        self.assertContains(cart_page, '400.00')

    def test_remove_from_cart(self):
        self.client.post(reverse('store:cart_add', kwargs={'product_id': self.product.id}), {'quantity': 1})
        self.client.post(reverse('store:cart_remove', kwargs={'product_id': self.product.id}))

        cart_page = self.client.get(reverse('store:cart'))
        self.assertContains(cart_page, 'Your shopping cart is empty')

    def test_add_more_than_available_stock(self):
        # Stock is 5; attempt to add 10
        response = self.client.post(reverse('store:cart_add', kwargs={'product_id': self.product.id}), {
            'quantity': 10
        })
        self.assertEqual(response.status_code, 302)

        # Cart should add only up to available stock (5)
        cart_page = self.client.get(reverse('store:cart'))
        self.assertContains(cart_page, 'value="5"')

    def test_add_out_of_stock_product(self):
        response = self.client.post(reverse('store:cart_add', kwargs={'product_id': self.out_of_stock_product.id}), {
            'quantity': 1
        })
        self.assertEqual(response.status_code, 302)

        cart_page = self.client.get(reverse('store:cart'))
        self.assertContains(cart_page, 'Your shopping cart is empty')

    def test_cart_add_bundle(self):
        """Test adding multiple products via bundle post."""
        product2 = Product.objects.create(
            category=self.category,
            name='Desk Mat',
            slug='desk-mat',
            price=Decimal('20.00'),
            stock=10,
            is_active=True
        )
        response = self.client.post(reverse('store:cart_add_bundle'), {
            'product_ids': [str(self.product.id), str(product2.id)],
        })
        self.assertEqual(response.status_code, 302)

        cart_page = self.client.get(reverse('store:cart'))
        self.assertEqual(cart_page.status_code, 200)
        self.assertContains(cart_page, 'Mechanical Keyboard')
        self.assertContains(cart_page, 'Desk Mat')

    def test_cart_add_ajax_quick_add(self):
        """Test AJAX response for quick add."""
        response = self.client.post(
            reverse('store:cart_add', kwargs={'product_id': self.product.id}),
            {'quantity': 1},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['cart_total_items'], 1)
        self.assertEqual(data['cart_total_price'], '100.00')


class CheckoutAndOrderTests(TestCase):
    """Test full checkout workflow, stock decrement, security, and atomicity."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='buyerpass123',
            first_name='Buyer',
            last_name='One'
        )
        self.other_user = User.objects.create_user(
            username='stranger',
            email='stranger@example.com',
            password='strangerpass123',
            first_name='Stranger',
            last_name='Two'
        )
        self.category = Category.objects.create(name='Gear', slug='gear')
        self.product = Product.objects.create(
            category=self.category,
            name='Titan Smartwatch',
            slug='titan-smartwatch',
            description='GPS watch.',
            price=Decimal('250.00'),
            stock=10,
            is_active=True
        )

    def test_checkout_requires_login(self):
        response = self.client.get(reverse('store:checkout'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('store:login'), response.url)

    def test_empty_cart_checkout_prevention(self):
        self.client.login(username='buyer', password='buyerpass123')
        response = self.client.get(reverse('store:checkout'))
        # Should redirect back to cart
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('store:cart'))

    def test_successful_order_placement_and_stock_reduction(self):
        self.client.login(username='buyer', password='buyerpass123')

        # Add 3 units of smartwatch to cart
        self.client.post(reverse('store:cart_add', kwargs={'product_id': self.product.id}), {'quantity': 3})

        # Post checkout form
        response = self.client.post(reverse('store:checkout'), {
            'full_name': 'Buyer One',
            'phone_number': '+1 555-0199',
            'address_line1': '742 Evergreen Terrace',
            'city': 'Springfield',
            'postal_code': '97477',
            'payment_method': 'COD',
        })
        self.assertEqual(response.status_code, 302)

        # Verify Order is created
        self.assertTrue(Order.objects.filter(user=self.user).exists())
        order = Order.objects.filter(user=self.user).first()
        self.assertEqual(order.total_amount, Decimal('750.00'))  # 3 * 250.00
        self.assertEqual(order.items.count(), 1)

        # Verify OrderItem snapshot values
        item = order.items.first()
        self.assertEqual(item.product_name, 'Titan Smartwatch')
        self.assertEqual(item.price, Decimal('250.00'))
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.subtotal, Decimal('750.00'))

        # Verify Stock reduction (10 - 3 = 7)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 7)

        # Verify Cart is cleared
        cart_page = self.client.get(reverse('store:cart'))
        self.assertContains(cart_page, 'Your shopping cart is empty')

        # Verify confirmation page renders
        conf_response = self.client.get(reverse('store:order_confirmation', kwargs={'order_number': order.order_number}))
        self.assertEqual(conf_response.status_code, 200)
        self.assertContains(conf_response, order.order_number)
        self.assertContains(conf_response, '750.00')

    def test_order_security_user_isolation(self):
        """Verify users cannot view or access another user's order."""
        # Buyer places an order
        self.client.login(username='buyer', password='buyerpass123')
        self.client.post(reverse('store:cart_add', kwargs={'product_id': self.product.id}), {'quantity': 1})
        self.client.post(reverse('store:checkout'), {
            'full_name': 'Buyer One',
            'phone_number': '1234567890',
            'address_line1': '123 Main St',
            'city': 'Town',
            'postal_code': '12345',
            'payment_method': 'COD',
        })
        order = Order.objects.get(user=self.user)

        # Log in as Stranger (User B)
        self.client.logout()
        self.client.login(username='stranger', password='strangerpass123')

        # Stranger attempts to view Buyer's order confirmation -> 404
        conf_response = self.client.get(reverse('store:order_confirmation', kwargs={'order_number': order.order_number}))
        self.assertEqual(conf_response.status_code, 404)

        # Stranger attempts to view Buyer's order detail -> 404
        detail_response = self.client.get(reverse('store:order_detail', kwargs={'order_number': order.order_number}))
        self.assertEqual(detail_response.status_code, 404)

    def test_insufficient_stock_rollback(self):
        """Verify transaction rollback when stock is insufficient at checkout time."""
        self.client.login(username='buyer', password='buyerpass123')
        # Add 5 items to cart
        self.client.post(reverse('store:cart_add', kwargs={'product_id': self.product.id}), {'quantity': 5})

        # Simultaneously simulate that product stock dropped to 2
        self.product.stock = 2
        self.product.save()

        # Buyer attempts checkout for 5 items
        response = self.client.post(reverse('store:checkout'), {
            'full_name': 'Buyer One',
            'phone_number': '1234567890',
            'address_line1': '123 Main St',
            'city': 'Town',
            'postal_code': '12345',
            'payment_method': 'COD',
        })
        # Should redirect back to cart with error
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('store:cart'))

        # Confirm no order was created
        self.assertFalse(Order.objects.filter(user=self.user).exists())
        # Confirm product stock remained unchanged at 2
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)


class Custom404PageTests(TestCase):
    """Test custom 404 error page."""

    def test_custom_404_renders(self):
        response = self.client.get('/this-path-does-not-exist-at-all/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'errors/404.html')
        self.assertContains(response, 'Page Not Found', status_code=404)


class ProductManagementWorkflowTests(TestCase):
    """Test full workflow of adding products, uploading images, storefront display, cart, and checkout."""

    def setUp(self):
        import io
        from PIL import Image as PilImage
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.client = Client()
        self.category = Category.objects.create(name='Gadgets', slug='gadgets')

        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staffadmin',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )

        # Create regular customer user
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@example.com',
            password='custpass123'
        )

    def _create_test_image(self, filename="test_item.jpg"):
        import io
        from PIL import Image as PilImage
        from django.core.files.uploadedfile import SimpleUploadedFile
        file_obj = io.BytesIO()
        img = PilImage.new("RGB", (120, 120), color=(15, 118, 110))
        img.save(file_obj, format="JPEG")
        file_obj.seek(0)
        return SimpleUploadedFile(filename, file_obj.read(), content_type="image/jpeg")

    def test_add_product_access_restricted_to_staff(self):
        # Anonymous user gets redirected to login
        response = self.client.get(reverse('store:add_product'))
        self.assertEqual(response.status_code, 302)

        # Regular user gets redirected to home with error
        self.client.login(username='customer1', password='custpass123')
        response = self.client.get(reverse('store:add_product'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('store:home'))

        # Staff user gets HTTP 200 and renders add_product form
        self.client.login(username='staffadmin', password='staffpass123')
        response = self.client.get(reverse('store:add_product'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/add_product.html')

    def test_add_product_with_image_and_full_storefront_lifecycle(self):
        self.client.login(username='staffadmin', password='staffpass123')
        test_img = self._create_test_image("studio_headphones.jpg")

        # 1. Post new product with uploaded image
        response = self.client.post(reverse('store:add_product'), {
            'name': 'Studio Wireless Pro Headphones',
            'category': self.category.id,
            'description': 'High fidelity active wireless headphones with ultra bass.',
            'price': '199.99',
            'stock': 15,
            'is_active': True,
            'image': test_img,
        })
        self.assertEqual(response.status_code, 302)

        # Product is created in database
        self.assertTrue(Product.objects.filter(slug='studio-wireless-pro-headphones').exists())
        product = Product.objects.get(slug='studio-wireless-pro-headphones')
        self.assertEqual(product.price, Decimal('199.99'))
        self.assertTrue(product.image.name.startswith('products/'))
        self.assertIn('.jpg', product.image.name)

        # 2. Check Home Page displays product and image
        home_resp = self.client.get(reverse('store:home'))
        self.assertEqual(home_resp.status_code, 200)
        self.assertContains(home_resp, 'Studio Wireless Pro Headphones')
        self.assertContains(home_resp, product.image.url)

        # 3. Check Product List & Search displays product and image
        list_resp = self.client.get(reverse('store:product_list') + '?q=Wireless+Pro')
        self.assertEqual(list_resp.status_code, 200)
        self.assertContains(list_resp, 'Studio Wireless Pro Headphones')
        self.assertContains(list_resp, product.image.url)

        # 4. Check Category Page displays product and image
        cat_resp = self.client.get(reverse('store:product_list_by_category', kwargs={'category_slug': 'gadgets'}))
        self.assertEqual(cat_resp.status_code, 200)
        self.assertContains(cat_resp, 'Studio Wireless Pro Headphones')
        self.assertContains(cat_resp, product.image.url)

        # 5. Check Product Detail Page displays main product image
        detail_resp = self.client.get(product.get_absolute_url())
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, product.image.url)

        # 6. Add product to cart and verify image in cart
        add_cart_resp = self.client.post(reverse('store:cart_add', kwargs={'product_id': product.id}), {'quantity': 1})
        self.assertEqual(add_cart_resp.status_code, 302)

        cart_resp = self.client.get(reverse('store:cart'))
        self.assertEqual(cart_resp.status_code, 200)
        self.assertContains(cart_resp, 'Studio Wireless Pro Headphones')
        self.assertContains(cart_resp, product.image.url)

        # 7. Check Checkout Page displays product image
        checkout_resp = self.client.get(reverse('store:checkout'))
        self.assertEqual(checkout_resp.status_code, 200)
        self.assertContains(checkout_resp, 'Studio Wireless Pro Headphones')
        self.assertContains(checkout_resp, product.image.url)

    def test_product_without_image_displays_clean_placeholder(self):
        # Create product with NO image
        prod_no_img = Product.objects.create(
            category=self.category,
            name='Minimalist Desk Organizer',
            slug='minimalist-desk-organizer',
            description='Wood desk organizer without image uploaded.',
            price=Decimal('24.50'),
            stock=8,
            is_active=True,
            image=None
        )
        self.assertEqual(prod_no_img.get_image_url, '/static/images/placeholder.svg')

        # Check detail page renders placeholder svg
        detail_resp = self.client.get(prod_no_img.get_absolute_url())
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, 'placeholder.svg')

        # Check catalog renders placeholder svg
        catalog_resp = self.client.get(reverse('store:product_list'))
        self.assertEqual(catalog_resp.status_code, 200)
        self.assertContains(catalog_resp, 'placeholder.svg')

    def test_product_form_validation(self):
        # Invalid price (<= 0)
        self.client.login(username='staffadmin', password='staffpass123')
        resp = self.client.post(reverse('store:add_product'), {
            'name': 'Bad Product',
            'category': self.category.id,
            'description': 'Description',
            'price': '-10.00',
            'stock': 5,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Product.objects.filter(name='Bad Product').exists())

