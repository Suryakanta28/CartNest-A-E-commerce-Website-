import os
import shutil
import django
from decimal import Decimal

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from store.models import Category, Product

source_dir = r'C:\Users\rsury\.gemini\antigravity-ide\brain\1ff0b745-3685-4d25-aeee-8b7cbdae8507\.user_uploaded'
dest_dir = r'c:\Users\rsury\Downloads\E-commerce\media\products'
os.makedirs(dest_dir, exist_ok=True)

mapping = [
    {
        'file': 'media_1792771991090.png',
        'target_name': 'tailored-oversized-blazer.png',
        'product_name': 'Tailored Oversized Wool-Blend Blazer',
        'category_slug': 'fashion',
        'price': Decimal('79.99'),
        'stock': 25,
        'description': (
            'A contemporary wardrobe staple. This relaxed-fit oversized blazer features '
            'structured shoulders, notched lapels, horn-effect buttons, and practical welt pockets. '
            'Crafted from a premium wrinkle-resistant wool-blend fabric, it effortlessly transitions '
            'from corporate meetings to casual weekend outings paired with denim and sneakers.'
        ),
    },
    {
        'file': 'media_1792772012239.png',
        'target_name': 'heavyweight-fleece-hoodie.png',
        'product_name': 'Heavyweight Fleece Minimalist Pullover Hoodie',
        'category_slug': 'fashion',
        'price': Decimal('54.99'),
        'stock': 40,
        'description': (
            'Engineered for exceptional warmth and everyday comfort. This premium streetwear hoodie '
            'is crafted from 450 GSM ultra-dense brushed organic cotton fleece. Features a double-layered '
            'hood with reinforced tonal drawstrings, seamless drop-shoulder drape, a spacious kangaroo '
            'front pocket, and heavy ribbed knit cuffs.'
        ),
    },
    {
        'file': 'media_1792772027395.png',
        'target_name': 'belted-safari-shirt-dress.png',
        'product_name': 'Vintage Belted Linen Safari Shirt Dress',
        'category_slug': 'fashion',
        'price': Decimal('69.99'),
        'stock': 30,
        'description': (
            'Effortless warm-weather elegance. This vintage-inspired safari midi dress is tailored from '
            '100% natural breathable linen-cotton. Designed with a structured point collar, rolled cap sleeves, '
            'button-flap utility chest pockets, full front button placket, and a detachable matching grommet belt.'
        ),
    },
    {
        'file': 'media_1792772041317.png',
        'target_name': 'kuleesh-purva-salwar-suit.png',
        'product_name': 'Kuleesh Purva Embroidered Silk Salwar Suit Set',
        'category_slug': 'fashion',
        'price': Decimal('89.99'),
        'stock': 18,
        'description': (
            "Exquisite festive craftsmanship from Vinay Fashion's Kuleesh Purva collection. This coral-peach "
            '3-piece designer ethnic ensemble features an intricately embroidered Chanderi silk kurta with floral '
            'Resham thread work, scalloped cutwork lace borders, tailored straight-fit trousers, and a diaphanous '
            'floral organza dupatta.'
        ),
    },
    {
        'file': 'media_1792772070811.png',
        'target_name': 'chikankari-embroidered-kurta.png',
        'product_name': 'Artisanal Chikankari Hand-Embroidered Silk Kurta',
        'category_slug': 'fashion',
        'price': Decimal('74.99'),
        'stock': 22,
        'description': (
            "A masterpiece of traditional heritage. This men's designer kurta is handcrafted from fine tussar "
            'silk-linen in a soft sandstone beige hue. Features intricate Chikankari and Aari floral needlework '
            'across the chest and cuffs, a split bandhgala neckline, and comfortable side slits. Perfect for weddings, '
            'festivities, and cultural celebrations.'
        ),
    }
]

fashion_cat, _ = Category.objects.get_or_create(slug='fashion', defaults={'name': 'Fashion'})

for item in mapping:
    src = os.path.join(source_dir, item['file'])
    dst = os.path.join(dest_dir, item['target_name'])
    shutil.copy2(src, dst)
    print(f"Copied {item['file']} -> {item['target_name']}")
    
    product, created = Product.objects.update_or_create(
        name=item['product_name'],
        defaults={
            'category': fashion_cat,
            'description': item['description'],
            'price': item['price'],
            'stock': item['stock'],
            'image': f"products/{item['target_name']}",
            'is_active': True,
        }
    )
    status = 'Created' if created else 'Updated'
    print(f"{status}: {product.name} (ID: {product.id}, Slug: {product.slug})")

print("All 5 products imported successfully!")
