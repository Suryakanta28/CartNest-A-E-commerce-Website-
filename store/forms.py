import os
import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Order


class UserRegisterForm(UserCreationForm):
    """User registration form with name, email, and password confirmation."""
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your last name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'name@example.com'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Choose a unique username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Create a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirm your password'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email


class UserLoginForm(AuthenticationForm):
    """Custom-styled login form."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information."""
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        user_pk = self.instance.pk
        if User.objects.filter(email=email).exclude(pk=user_pk).exists():
            raise forms.ValidationError("Another account is already using this email.")
        return email


class AddToCartForm(forms.Form):
    """Form to select item quantity when adding to cart."""
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'quantity-input',
            'min': '1',
            'value': '1'
        })
    )


class CheckoutForm(forms.Form):
    """Order checkout form with server-side shipping and contact validation."""
    full_name = forms.CharField(
        max_length=150,
        required=True,
        label="Full Name",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. John Doe'
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. +1 555-0199 or 9876543210'
        })
    )
    address_line1 = forms.CharField(
        max_length=255,
        required=True,
        label="Street Address",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. 123 Main Street, Apt 4B'
        })
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        label="City",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. New York'
        })
    )
    postal_code = forms.CharField(
        max_length=20,
        required=True,
        label="Postal / ZIP Code",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. 10001'
        })
    )
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        initial=Order.PAYMENT_COD,
        widget=forms.RadioSelect(attrs={'class': 'payment-radio'})
    )

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        # Ensure phone number contains at least 7 digits
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 7:
            raise forms.ValidationError("Please provide a valid phone number with at least 7 digits.")
        return phone

    def clean_postal_code(self):
        postal = self.cleaned_data.get('postal_code', '').strip()
        if len(postal) < 3:
            raise forms.ValidationError("Please enter a valid postal or ZIP code.")
        return postal


class ProductForm(forms.ModelForm):
    """Form for staff/admin to add new products from the web interface."""
    name = forms.CharField(
        max_length=200,
        required=True,
        label="Product Name",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. UltraSlim Pro 14" Developer Laptop',
            'autocomplete': 'off',
        })
    )
    category = forms.ModelChoiceField(
        queryset=None,  # Populated dynamically in __init__
        required=True,
        empty_label="-- Select a Category --",
        label="Product Category",
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    description = forms.CharField(
        required=True,
        label="Product Description",
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 4,
            'placeholder': 'Provide detailed product specifications, materials, and features...',
        })
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        required=True,
        label="Price (₹)",
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. 149.99',
            'step': '0.01',
            'min': '0.01',
        })
    )
    stock = forms.IntegerField(
        min_value=0,
        initial=10,
        required=True,
        label="Stock Quantity",
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. 25',
            'min': '0',
        })
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label="Publish immediately (Active Status)",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox',
        })
    )
    image = forms.ImageField(
        required=False,
        label="Product Image",
        widget=forms.FileInput(attrs={
            'class': 'form-file-input',
            'accept': 'image/jpeg,image/png,image/webp,image/avif',
            'id': 'product-image-upload',
        }),
        help_text="Select a JPG, PNG, or WEBP image from your device (Max 5MB)."
    )

    class Meta:
        from .models import Product
        model = Product
        fields = ['name', 'category', 'description', 'price', 'stock', 'image', 'is_active']

    def __init__(self, *args, **kwargs):
        from .models import Category
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all().order_by('name')

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError("Product name must be at least 2 characters long.")
        return name

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Product price must be greater than zero.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError("Stock quantity cannot be negative.")
        return stock

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image

        # 1. File size check: Max 5 MB
        max_size_mb = 5
        if image.size > max_size_mb * 1024 * 1024:
            raise forms.ValidationError(f"The uploaded image is too large ({image.size / (1024*1024):.1f}MB). Maximum allowed size is {max_size_mb}MB.")

        # 2. File extension check
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.avif']
        ext = os.path.splitext(image.name)[1].lower() if hasattr(image, 'name') else ''
        if ext and ext not in valid_extensions:
            raise forms.ValidationError(f"Unsupported file format '{ext}'. Allowed formats are JPG, PNG, WEBP, and AVIF.")

        # 3. Pillow image integrity validation
        try:
            from PIL import Image as PilImage
            image.seek(0)
            img = PilImage.open(image)
            img.verify()
            image.seek(0)
        except Exception:
            raise forms.ValidationError("Uploaded file is corrupted or not a valid image.")

        return image
