import os
from decimal import Decimal
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from store.models import Category, Product, ProductImage
from PIL import Image, ImageDraw, ImageFont


class Command(BaseCommand):
    help = "Populates database with sample categories, products, images, and demo accounts."

    def create_placeholder_image(self, filename, title, bg_color=(30, 41, 59), accent_color=(99, 102, 241)):
        """Generate a sleek, modern product placeholder image using Pillow."""
        media_products_dir = Path(settings.MEDIA_ROOT) / 'products'
        media_products_dir.mkdir(parents=True, exist_ok=True)
        filepath = media_products_dir / filename
        if filepath.exists() and filepath.stat().st_size > 1000:
            return f"products/{filename}"

        width, height = 600, 600
        image = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(image)

        # Draw decorative gradient-like circular accents
        draw.ellipse([(-50, -50), (250, 250)], fill=(bg_color[0]+20, bg_color[1]+20, bg_color[2]+30))
        draw.ellipse([(350, 350), (650, 650)], fill=(bg_color[0]+15, bg_color[1]+15, bg_color[2]+25))

        # Draw product card container
        card_box = [(80, 80), (520, 520)]
        draw.rounded_rectangle(card_box, radius=24, outline=accent_color, width=3, fill=(bg_color[0]+10, bg_color[1]+10, bg_color[2]+15))

        # Draw accent icon / badge circle
        badge_box = [(250, 160), (350, 260)]
        draw.ellipse(badge_box, fill=accent_color)

        # Try to load default font
        try:
            font_large = ImageFont.load_default(size=24)
            font_small = ImageFont.load_default(size=16)
        except TypeError:
            # Fallback for older Pillow versions
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Center product title
        # Text wrapping
        words = title.split()
        lines = []
        cur_line = []
        for word in words:
            cur_line.append(word)
            if len(" ".join(cur_line)) > 18:
                lines.append(" ".join(cur_line))
                cur_line = []
        if cur_line:
            lines.append(" ".join(cur_line))

        y_offset = 320
        for line in lines:
            draw.text((width // 2, y_offset), line, fill=(255, 255, 255), anchor="mm", font=font_large)
            y_offset += 32

        draw.text((width // 2, 450), "PREMIUM QUALITY", fill=accent_color, anchor="mm", font=font_small)

        image.save(filepath, format="JPEG", quality=90)
        return f"products/{filename}"

    def handle(self, *args, **options):
        self.stdout.write("Seeding sample categories and products...")

        # 1. Create Superuser & Demo User
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS("Created superuser: admin / admin123"))
        else:
            self.stdout.write("Superuser 'admin' already exists.")

        if not User.objects.filter(username='demouser').exists():
            demo_user = User.objects.create_user(
                username='demouser',
                email='demouser@example.com',
                password='demo123',
                first_name='Jane',
                last_name='Doe'
            )
            self.stdout.write(self.style.SUCCESS("Created demo customer: demouser / demo123"))
        else:
            self.stdout.write("Demo customer 'demouser' already exists.")

        # 2. Categories
        categories_data = [
            {
                'name': 'Electronics',
                'description': 'Smart wearables, wireless audio devices, mechanical keyboards, and gadgets.',
                'slug': 'electronics',
                'image': 'categories/electronics.jpg',
            },
            {
                'name': 'Home & Living',
                'description': 'Thoughtful workspace setups, monitor lighting, and home essentials.',
                'slug': 'home-living',
                'image': 'categories/home-living.jpg',
            },
            {
                'name': 'Fashion',
                'description': 'Minimalist bags, handcrafted leather cardholders, and outdoor lifestyle essentials.',
                'slug': 'fashion',
                'image': 'categories/fashion.jpg',
            },
            {
                'name': 'Accessories',
                'description': 'Everyday charging gear, desk pads, organizers, and durable cables.',
                'slug': 'accessories',
                'image': 'categories/accessories.jpg',
            },
        ]

        category_objs = {}
        for cat_info in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=cat_info['slug'],
                defaults={'name': cat_info['name'], 'description': cat_info['description'], 'image': cat_info['image']}
            )
            cat.name = cat_info['name']
            cat.image = cat_info['image']
            cat.save()
            category_objs[cat.slug] = cat

        # 3. Products
        products_data = [
            {
                'category': 'audio-headphones',
                'name': 'Aura Studio Wireless ANC Headphones',
                'slug': 'aura-studio-wireless-anc-headphones',
                'price': Decimal('199.99'),
                'stock': 25,
                'description': 'Experience sound in its purest form with 40mm beryllium drivers, active hybrid noise cancellation, 45 hours battery life, and ultra-plush memory foam cushions.',
                'img_file': 'aura-headphones.jpg',
                'bg_color': (15, 23, 42),
                'accent_color': (99, 102, 241),
            },
            {
                'category': 'audio-headphones',
                'name': 'SonicPulse Pro True Wireless Earbuds',
                'slug': 'sonicpulse-pro-earbuds',
                'price': Decimal('89.50'),
                'stock': 40,
                'description': 'Ultra-compact earbuds featuring IPX7 water resistance, transparent pass-through mode, intuitive touch controls, and 30 hours of playback with the wireless charging case.',
                'img_file': 'sonicpulse-earbuds.jpg',
                'bg_color': (24, 24, 27),
                'accent_color': (14, 165, 233),
            },
            {
                'category': 'audio-headphones',
                'name': 'Verve Hi-Fi Desktop Soundbar',
                'slug': 'verve-hifi-desktop-soundbar',
                'price': Decimal('129.00'),
                'stock': 18,
                'description': 'Sleek soundbar engineered specifically for PC and monitor setups. Features dual passive radiators, Bluetooth 5.3, USB-C input, and customizable ambient backlighting.',
                'img_file': 'verve-soundbar.jpg',
                'bg_color': (20, 20, 20),
                'accent_color': (244, 63, 94),
            },
            {
                'category': 'smart-tech-gadgets',
                'name': 'Chronos Titan GPS Smartwatch',
                'slug': 'chronos-titan-smartwatch',
                'price': Decimal('249.99'),
                'stock': 15,
                'description': 'Rugged aerospace-grade titanium bezel with AMOLED sapphire display. 14-day battery life, heart-rate and SpO2 tracking, multi-band GPS, and sleep analysis.',
                'img_file': 'chronos-smartwatch.jpg',
                'bg_color': (30, 27, 75),
                'accent_color': (168, 85, 247),
            },
            {
                'category': 'smart-tech-gadgets',
                'name': 'Apex 75 Mechanical Keyboard',
                'slug': 'apex-75-mechanical-keyboard',
                'price': Decimal('149.00'),
                'stock': 22,
                'description': 'Custom CNC aluminum 75% mechanical keyboard with hot-swappable tactile switches, gasket mount design, sound-dampening silicone foam, and south-facing RGB.',
                'img_file': 'apex-keyboard.jpg',
                'bg_color': (15, 30, 45),
                'accent_color': (16, 185, 129),
            },
            {
                'category': 'accessories',
                'name': 'AeroCharge MagSafe Wireless Dock',
                'slug': 'aerocharge-magsafe-dock',
                'price': Decimal('59.99'),
                'stock': 35,
                'description': '3-in-1 fast wireless charging stand for smartphone, smartwatch, and earbuds. Weighted zinc alloy base with non-slip silicone pads and safe temperature protection.',
                'img_file': 'aerocharge-dock.jpg',
                'bg_color': (23, 23, 23),
                'accent_color': (245, 158, 11),
            },
            {
                'category': 'lifestyle-apparel',
                'name': 'Nomad Explorer Waterproof Tech Backpack',
                'slug': 'nomad-explorer-tech-backpack',
                'price': Decimal('119.00'),
                'stock': 20,
                'description': 'Weatherproof Cordura exterior with dedicated 16-inch fleece-lined laptop sleeve, magnetic Fidlock buckles, luggage passthrough, and ergonomic back ventilation.',
                'img_file': 'nomad-backpack.jpg',
                'bg_color': (41, 37, 36),
                'accent_color': (217, 119, 6),
            },
            {
                'category': 'lifestyle-apparel',
                'name': 'Minimalist Leather Slim Cardholder',
                'slug': 'minimalist-leather-cardholder',
                'price': Decimal('34.99'),
                'stock': 50,
                'description': 'Handcrafted full-grain Italian leather card wallet with RFID blocking technology, quick-access pull tab, and storage for up to 8 cards plus folded cash.',
                'img_file': 'leather-cardholder.jpg',
                'bg_color': (45, 30, 20),
                'accent_color': (251, 146, 60),
            },
            {
                'category': 'home-workspace',
                'name': 'Lumina Pro Screenbar Monitor Light',
                'slug': 'lumina-pro-monitor-lightbar',
                'price': Decimal('69.50'),
                'stock': 30,
                'description': 'Asymmetrical optical design that illuminates your desk with zero screen glare. Features wireless rotary dial control, stepless color temperature adjustment, and auto-dimming.',
                'img_file': 'lumina-lightbar.jpg',
                'bg_color': (17, 24, 39),
                'accent_color': (59, 130, 246),
            },
            {
                'category': 'home-workspace',
                'name': 'ErgoLift Solid Walnut Laptop Stand',
                'slug': 'ergolift-walnut-laptop-stand',
                'price': Decimal('54.00'),
                'stock': 28,
                'description': 'Elevates your laptop to eye level for optimal posture. Precision carved from sustainable American black walnut with brushed aluminum feet and protective silicone lining.',
                'img_file': 'ergolift-stand.jpg',
                'bg_color': (38, 25, 18),
                'accent_color': (249, 115, 22),
            },
            {
                'category': 'home-workspace',
                'name': 'HydroGlow Smart Thermal Water Bottle',
                'slug': 'hydroglow-smart-bottle',
                'price': Decimal('42.00'),
                'stock': 45,
                'description': 'Vacuum insulated 650ml stainless steel flask with integrated LED touch temperature readout and hourly hydration reminder ring. Keeps drinks cold for 24h, hot for 12h.',
                'img_file': 'hydroglow-bottle.jpg',
                'bg_color': (19, 35, 47),
                'accent_color': (6, 182, 212),
            },
            {
                'category': 'audio-headphones',
                'name': 'Pulse Mini Portable Outdoor Speaker',
                'slug': 'pulse-mini-portable-speaker',
                'price': Decimal('49.99'),
                'stock': 60,
                'description': 'Pocket-sized powerhouse delivering 360-degree immersive sound and punching bass. Features IP67 dust/waterproof rating, carabiner strap, and 12-hour battery life.',
                'img_file': 'pulse-speaker.jpg',
                'bg_color': (30, 41, 59),
                'accent_color': (139, 92, 246),
            },
            {
                'category': 'accessories',
                'name': 'Apex Aluminum Desktop Headphone Stand',
                'slug': 'apex-headphone-stand',
                'price': Decimal('29.99'),
                'stock': 35,
                'description': 'Crafted from solid aircraft-grade aluminum with weighted base and silicone padding. Keeps your premium headphones organized and safely displayed.',
                'img_file': 'headphone-stand.jpg',
                'bg_color': (24, 24, 27),
                'accent_color': (99, 102, 241),
            },
            {
                'category': 'accessories',
                'name': 'AeroLink Braided Audio Cable with Mic',
                'slug': 'aerolink-braided-audio-cable',
                'price': Decimal('16.50'),
                'stock': 50,
                'description': 'Gold-plated 3.5mm jack with oxygen-free copper core and reinforced tangle-free braided exterior for crystal-clear audio transmission.',
                'img_file': 'braided-cable.jpg',
                'bg_color': (15, 23, 42),
                'accent_color': (6, 182, 212),
            },
            {
                'category': 'accessories',
                'name': 'Aegis Hard-Shell Protective Travel Case',
                'slug': 'aegis-headphone-travel-case',
                'price': Decimal('24.99'),
                'stock': 40,
                'description': 'Shockproof and water-resistant EVA hard shell with soft velvet interior lining, cable storage compartment, and heavy-duty metal zipper.',
                'img_file': 'travel-case.jpg',
                'bg_color': (30, 41, 59),
                'accent_color': (168, 85, 247),
            },
            {
                'category': 'accessories',
                'name': 'VoltCraft 65W GaN Dual-Port Fast Charger',
                'slug': 'voltcraft-65w-gan-charger',
                'price': Decimal('34.99'),
                'stock': 45,
                'description': 'Next-gen Gallium Nitride tech delivers ultra-fast 65W charging for laptops, tablets, and phones simultaneously in a 50% smaller footprint.',
                'img_file': 'gan-charger.jpg',
                'bg_color': (17, 24, 39),
                'accent_color': (245, 158, 11),
            },
            {
                'category': 'accessories',
                'name': 'GlideTrack Pro Anti-Fray Desk Mat',
                'slug': 'glidetrack-pro-desk-mat',
                'price': Decimal('22.00'),
                'stock': 55,
                'description': '900x400mm extended surface with micro-woven cloth texture, water-repellent coating, 4mm plush cushioning, and non-slip rubber base.',
                'img_file': 'desk-mat.jpg',
                'bg_color': (15, 23, 42),
                'accent_color': (16, 185, 129),
            },
            {
                'category': 'accessories',
                'name': 'OrbitMag 10000mAh Magnetic Power Bank',
                'slug': 'orbitmag-magnetic-powerbank',
                'price': Decimal('49.99'),
                'stock': 30,
                'description': 'Snap-on 15W wireless power bank with 20W PD USB-C bidirectional fast charging and foldable kickstand for hands-free video watching.',
                'img_file': 'magnetic-powerbank.jpg',
                'bg_color': (24, 24, 27),
                'accent_color': (59, 130, 246),
            },
            {
                'category': 'lifestyle-apparel',
                'name': 'Solaris Matte Black Polarized Sunglasses',
                'slug': 'solaris-matte-sunglasses',
                'price': Decimal('39.00'),
                'stock': 35,
                'description': 'Ultra-lightweight TR90 frame with TAC polarized UV400 lenses that eliminate glare and provide crisp optical clarity for all outdoor adventures.',
                'img_file': 'sunglasses.jpg',
                'bg_color': (28, 25, 23),
                'accent_color': (217, 119, 6),
            },
            {
                'category': 'accessories',
                'name': 'AeroPack Weatherproof Gear Organizer Pouch',
                'slug': 'aeropack-organizer-pouch',
                'price': Decimal('28.50'),
                'stock': 40,
                'description': 'Origami-style accordion storage pockets for cables, chargers, memory cards, and power adapters with YKK weatherproof zippers.',
                'img_file': 'tech-pouch.jpg',
                'bg_color': (41, 37, 36),
                'accent_color': (249, 115, 22),
            },
            {
                'category': 'accessories',
                'name': 'CableSnap Magnetic Desk Organizer 5-Pack',
                'slug': 'cablesnap-magnetic-organizer',
                'price': Decimal('14.99'),
                'stock': 70,
                'description': 'Keep charging and power cables neatly anchored to your desk edge with strong neodymium magnets and residue-free adhesive backing.',
                'img_file': 'cable-organizer.jpg',
                'bg_color': (30, 41, 59),
                'accent_color': (6, 182, 212),
            },
            {
                'category': 'home-workspace',
                'name': 'AmbientGlow Smart Desk Accent Lightstrip',
                'slug': 'ambientglow-desk-lightstrip',
                'price': Decimal('26.00'),
                'stock': 35,
                'description': '2-meter USB-powered RGBIC ambient LED strip with wireless remote, dynamic music sync modes, and subtle diffuse under-desk backlighting.',
                'img_file': 'desk-lightstrip.jpg',
                'bg_color': (15, 23, 42),
                'accent_color': (236, 72, 153),
            },
            {
                'category': 'electronics',
                'name': 'UltraSlim Pro 14" Developer Laptop',
                'slug': 'ultraslim-pro-14-laptop',
                'price': Decimal('999.00'),
                'stock': 12,
                'description': 'Flagship ultraportable developer laptop featuring a 3.2K 120Hz OLED screen, aluminum unibody construction, backlit keyboard, all-day battery life, and rapid USB-C charging.',
                'img_file': 'pro-laptop.jpg',
                'bg_color': (15, 23, 42),
                'accent_color': (14, 165, 233),
            },
            {
                'category': 'fashion',
                'name': 'Classic Organic Cotton Crewneck T-Shirt',
                'slug': 'classic-crewneck-tshirt',
                'price': Decimal('29.99'),
                'stock': 50,
                'description': 'Handcrafted from 100% GOTS-certified heavyweight combed organic cotton. Features double-stitched seams, relaxed tailored fit, and pre-shrunk breathable fabric for all-day comfort.',
                'img_file': 'crewneck-tshirt.jpg',
                'bg_color': (24, 24, 27),
                'accent_color': (245, 158, 11),
            },
            {
                'category': 'fashion',
                'name': 'StrideFlow All-Day Comfort Running Shoes',
                'slug': 'strideflow-comfort-shoes',
                'price': Decimal('89.00'),
                'stock': 28,
                'description': 'Engineered knit upper with responsive cloud-foam cushioning, ergonomic arch support, high-traction rubber outsole, and lightweight breathable silhouette.',
                'img_file': 'comfort-sneakers.jpg',
                'bg_color': (30, 41, 59),
                'accent_color': (16, 185, 129),
            },
            {
                'category': 'home-living',
                'name': 'Ceramic Artisan Matte Coffee Mug',
                'slug': 'ceramic-artisan-coffee-mug',
                'price': Decimal('19.50'),
                'stock': 45,
                'description': 'Hand-thrown stoneware ceramic mug with tactile matte finish, comfortable ergonomic handle, and heat-retaining thick walls. Microwave and dishwasher safe.',
                'img_file': 'artisan-coffee-mug.jpg',
                'bg_color': (41, 37, 36),
                'accent_color': (217, 119, 6),
            },
            # --- New Fashion Products ---
            {
                'category': 'fashion',
                'name': 'Merino Wool Minimalist Beanie',
                'slug': 'merino-wool-minimalist-beanie',
                'price': Decimal('24.99'),
                'stock': 40,
                'description': 'Fine-spun 100% Australian merino wool ribbed knit beanie with breathable warmth, temperature regulation, and clean roll-up cuff.',
                'img_file': 'merino-beanie.jpg',
                'bg_color': (30, 41, 59),
                'accent_color': (14, 165, 233),
            },
            {
                'category': 'fashion',
                'name': 'Vintage Washed Denim Jacket',
                'slug': 'vintage-washed-denim-jacket',
                'price': Decimal('89.99'),
                'stock': 25,
                'description': 'Classic silhouette crafted from 13.5oz ring-spun denim with distressed brass hardware, dual chest pockets, and relaxed tailored drape.',
                'img_file': 'denim-jacket.jpg',
                'bg_color': (24, 24, 27),
                'accent_color': (59, 130, 246),
            },
            {
                'category': 'fashion',
                'name': 'Classic Canvas Weekender Duffel Bag',
                'slug': 'canvas-weekender-duffel-bag',
                'price': Decimal('79.50'),
                'stock': 20,
                'description': 'Heavy-duty 16oz waxed cotton canvas duffel with genuine full-grain leather straps, padded shoulder sling, and roomy 42L capacity.',
                'img_file': 'canvas-duffel.jpg',
                'bg_color': (41, 37, 36),
                'accent_color': (217, 119, 6),
            },
            {
                'category': 'fashion',
                'name': 'Handwoven Linen Summer Scarf',
                'slug': 'handwoven-linen-summer-scarf',
                'price': Decimal('32.00'),
                'stock': 35,
                'description': 'Airy, featherlight pure Belgian linen scarf with raw frayed edges. Perfect for transitioning seasons with effortless drape and soft touch.',
                'img_file': 'linen-scarf.jpg',
                'bg_color': (28, 25, 23),
                'accent_color': (245, 158, 11),
            },
            # --- New Accessories Products ---
            {
                'category': 'accessories',
                'name': 'Titanium Carabiner EDC Keychain',
                'slug': 'titanium-carabiner-edc-keychain',
                'price': Decimal('18.00'),
                'stock': 65,
                'description': 'Precision CNC-machined Grade 5 titanium carabiner with integrated bottle opener, pry tip, and secure dual-gate key retention system.',
                'img_file': 'edc-keychain.jpg',
                'bg_color': (15, 23, 42),
                'accent_color': (16, 185, 129),
            },
            {
                'category': 'accessories',
                'name': 'MagLock Ultra-Slim Phone Wallet',
                'slug': 'maglock-ultra-slim-wallet',
                'price': Decimal('28.00'),
                'stock': 45,
                'description': 'Magnetic snap-on cardholder crafted from oil-waxed vegan leather. Holds 3 essential cards with RFID shielding and foldable viewing kickstand.',
                'img_file': 'magnetic-wallet.jpg',
                'bg_color': (24, 24, 27),
                'accent_color': (168, 85, 247),
            },
            {
                'category': 'accessories',
                'name': 'Anodized Aluminum Laptop Riser Bar',
                'slug': 'anodized-aluminum-laptop-riser',
                'price': Decimal('35.00'),
                'stock': 30,
                'description': 'Ergonomic 15-degree wedge stand milled from solid aluminum alloy for improved typing posture and optimal laptop bottom airflow.',
                'img_file': 'aluminum-riser.jpg',
                'bg_color': (15, 23, 42),
                'accent_color': (6, 182, 212),
            },
            {
                'category': 'accessories',
                'name': 'Silicone AirTag Protective Case 4-Pack',
                'slug': 'silicone-airtag-protective-case-pack',
                'price': Decimal('15.99'),
                'stock': 80,
                'description': 'Liquid silicone protective holders with rustproof stainless steel keyrings. Scratch-resistant, washable, and signal-transparent.',
                'img_file': 'airtag-case.jpg',
                'bg_color': (30, 41, 59),
                'accent_color': (236, 72, 153),
            },
            # --- New Electronics Products ---
            {
                'category': 'electronics',
                'name': 'VividLens 4K Ultra-HD Webcam',
                'slug': 'vividlens-4k-ultra-hd-webcam',
                'price': Decimal('79.99'),
                'stock': 20,
                'description': 'High-clarity 4K sensor at 30fps with autofocus, AI noise-filtering dual microphones, privacy shutter, and universal tripod threading.',
                'img_file': '4k-webcam.jpg',
                'bg_color': (15, 23, 42),
                'accent_color': (14, 165, 233),
            },
            {
                'category': 'electronics',
                'name': 'HyperGlide Ergonomic Wireless Mouse',
                'slug': 'hyperglide-ergonomic-wireless-mouse',
                'price': Decimal('54.00'),
                'stock': 35,
                'description': 'Vertical ergonomic palm grip designed to relieve wrist strain. 4000 DPI optical tracking, whisper-quiet clicks, and multi-device Bluetooth.',
                'img_file': 'wireless-mouse.jpg',
                'bg_color': (24, 24, 27),
                'accent_color': (16, 185, 129),
            },
            {
                'category': 'electronics',
                'name': 'StreamPod Studio USB Condenser Microphone',
                'slug': 'streampod-studio-usb-microphone',
                'price': Decimal('69.00'),
                'stock': 25,
                'description': 'Cardioid polar pattern microphone featuring zero-latency headphone monitoring, quick tap-to-mute sensor, and heavy anti-vibration stand.',
                'img_file': 'studio-microphone.jpg',
                'bg_color': (17, 24, 39),
                'accent_color': (244, 63, 94),
            },
            {
                'category': 'electronics',
                'name': 'NovaPad 10.5" Android Tablet',
                'slug': 'novapad-10-android-tablet',
                'price': Decimal('189.00'),
                'stock': 15,
                'description': 'Brilliant 10.5-inch 2K IPS display, octa-core processor, 64GB expandable storage, stereo speakers, and slim aluminum body.',
                'img_file': 'android-tablet.jpg',
                'bg_color': (15, 23, 42),
                'accent_color': (99, 102, 241),
            },
            # --- New Home & Living Products ---
            {
                'category': 'home-living',
                'name': 'AromaMist Ceramic Ultrasonic Diffuser',
                'slug': 'aromamist-ceramic-ultrasonic-diffuser',
                'price': Decimal('38.50'),
                'stock': 30,
                'description': 'Handcrafted matte ceramic cover with whisper-quiet ultrasonic misting, 7 soothing ambient light tones, and auto-shutoff timer.',
                'img_file': 'ceramic-diffuser.jpg',
                'bg_color': (30, 41, 59),
                'accent_color': (168, 85, 247),
            },
            {
                'category': 'home-living',
                'name': 'PureComfort Memory Foam Lumbar Cushion',
                'slug': 'purecomfort-memory-foam-lumbar-cushion',
                'price': Decimal('34.00'),
                'stock': 40,
                'description': 'Orthopedic contoured memory foam pillow designed to support spinal alignment during long work or study sessions. Breathable 3D mesh cover.',
                'img_file': 'lumbar-cushion.jpg',
                'bg_color': (15, 23, 42),
                'accent_color': (6, 182, 212),
            },
            {
                'category': 'home-living',
                'name': 'Minimalist Concrete Succulent Planter',
                'slug': 'minimalist-concrete-succulent-planter',
                'price': Decimal('22.00'),
                'stock': 50,
                'description': 'Cast geometric concrete pot with natural drainage hole and protective cork bottom pad. Modern architectural accent for any desk.',
                'img_file': 'concrete-planter.jpg',
                'bg_color': (24, 24, 27),
                'accent_color': (16, 185, 129),
            },
            {
                'category': 'home-living',
                'name': 'Nordic Bamboo Desk Table Lamp',
                'slug': 'nordic-bamboo-desk-table-lamp',
                'price': Decimal('46.00'),
                'stock': 24,
                'description': 'Warm minimalist table lamp featuring natural bamboo base, frosted linen shade, touch dimmer, and built-in USB charging port.',
                'img_file': 'bamboo-lamp.jpg',
                'bg_color': (41, 37, 36),
                'accent_color': (245, 158, 11),
            },
        ]

        cat_slug_map = {
            'audio-headphones': 'electronics',
            'smart-tech-gadgets': 'electronics',
            'lifestyle-apparel': 'fashion',
            'home-workspace': 'home-living',
            'accessories-charging': 'accessories',
            'accessories': 'accessories',
            'electronics': 'electronics',
            'fashion': 'fashion',
            'home-living': 'home-living',
        }

        for p_data in products_data:
            cat_key = p_data['category']
            actual_cat_slug = cat_slug_map.get(cat_key, cat_key)
            cat = category_objs.get(actual_cat_slug) or list(category_objs.values())[0]

            img_rel_path = self.create_placeholder_image(
                p_data['img_file'],
                p_data['name'],
                p_data['bg_color'],
                p_data['accent_color']
            )

            product, created = Product.objects.update_or_create(
                slug=p_data['slug'],
                defaults={
                    'category': cat,
                    'name': p_data['name'],
                    'price': p_data['price'],
                    'stock': p_data['stock'],
                    'description': p_data['description'],
                    'image': img_rel_path,
                    'is_active': True,
                }
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} product: {product.name} (${product.price})")

        # 4. Seed gallery photos for showcase items
        flagship = Product.objects.filter(slug='aura-studio-wireless-anc-headphones').first()
        if flagship:
            ProductImage.objects.get_or_create(
                product=flagship,
                image='products/gallery/aura-detail.jpg',
                defaults={'alt_text': 'Cushion and Titanium Hinge Detail', 'order': 1}
            )
            ProductImage.objects.get_or_create(
                product=flagship,
                image='products/gallery/aura-lifestyle.jpg',
                defaults={'alt_text': 'Workspace Desk Setup View', 'order': 2}
            )

        smartwatch = Product.objects.filter(slug='chronos-titan-smartwatch').first()
        if smartwatch:
            ProductImage.objects.get_or_create(
                product=smartwatch,
                image='products/gallery/chronos-detail.jpg',
                defaults={'alt_text': 'Sensor Array & Titanium Back Profile', 'order': 1}
            )

        keyboard = Product.objects.filter(slug='apex-75-mechanical-keyboard').first()
        if keyboard:
            ProductImage.objects.get_or_create(
                product=keyboard,
                image='products/gallery/apex-detail.jpg',
                defaults={'alt_text': 'PBT Keycaps & Tactile Mechanical Switch Detail', 'order': 1}
            )
            self.stdout.write("Configured multi-image galleries for showcase items.")

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
