from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'products_count', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'Total Products'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'order')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'thumbnail_preview',
        'name',
        'category',
        'price',
        'stock',
        'is_active',
        'gallery_count',
        'created_at',
    )
    list_display_links = ('name', 'thumbnail_preview')
    list_editable = ('price', 'stock', 'is_active')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    list_per_page = 20

    fieldsets = (
        ('Product Identification', {
            'fields': ('name', 'slug', 'category', 'description'),
            'description': 'Enter the essential product details. Slug will auto-generate from the product name.',
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock', 'is_active'),
            'description': 'Set pricing, available quantity in stock, and toggle active status for the storefront.',
        }),
        ('Product Image Upload', {
            'fields': ('image', 'current_image_display'),
            'description': 'Upload a product image from your computer (saved to media/products/). Supported formats: JPG, PNG, WEBP.',
        }),
    )
    readonly_fields = ('current_image_display',)

    def thumbnail_preview(self, obj):
        if obj.image:
            try:
                return format_html(
                    '<img src="{}" style="width: 48px; height: 48px; object-fit: cover; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.08);" />',
                    obj.image.url
                )
            except ValueError:
                pass
        return format_html(
            '<img src="/static/images/placeholder.svg" style="width: 48px; height: 48px; object-fit: contain; border-radius: 8px; background: #f1f5f9; padding: 4px;" title="Default Placeholder" />'
        )
    thumbnail_preview.short_description = 'Image'

    def current_image_display(self, obj):
        if obj.image:
            try:
                return format_html(
                    '<div style="display:flex; align-items:center; gap: 1rem;">'
                    '<img src="{}" style="max-height: 140px; max-width: 180px; object-fit: cover; border-radius: 8px; border: 1px solid #cbd5e1; box-shadow: 0 2px 8px rgba(0,0,0,0.08);" />'
                    '<div><p style="margin:0 0 4px; font-weight:600; color:#0f766e;">Currently Uploaded</p>'
                    '<a href="{}" target="_blank" style="font-size:0.85rem; color:#0284c7;">View Full Resolution &rarr;</a></div>'
                    '</div>',
                    obj.image.url,
                    obj.image.url
                )
            except ValueError:
                pass
        return format_html(
            '<div style="display:flex; align-items:center; gap: 1rem;">'
            '<img src="/static/images/placeholder.svg" style="max-height: 100px; max-width: 120px; object-fit: contain; border-radius: 8px; background: #f8fafc; border: 1px dashed #cbd5e1; padding: 8px;" />'
            '<p style="margin:0; color:#64748b; font-size:0.9rem;">No custom image uploaded yet. A clean placeholder is currently shown on the storefront.</p>'
            '</div>'
        )
    current_image_display.short_description = 'Current Image Preview'

    def gallery_count(self, obj):
        count = obj.gallery_images.count()
        return format_html('<span style="font-weight: 600; color: #475569;">{} photos</span>', count)
    gallery_count.short_description = 'Gallery'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'price', 'quantity', 'subtotal')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'user',
        'full_name',
        'phone_number',
        'total_amount',
        'status',
        'payment_method',
        'created_at',
    )
    list_editable = ('status',)
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = (
        'order_number',
        'full_name',
        'phone_number',
        'address_line1',
        'city',
        'user__username',
        'user__email',
    )
    readonly_fields = ('order_number', 'total_amount', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    list_per_page = 20
