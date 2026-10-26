# Nexus E-Commerce Store

A modern, full-stack, beginner-friendly E-commerce Store web application built with **Python 3**, **Django**, **Django Templates**, **Vanilla CSS3**, and **Vanilla JavaScript** (without React, Next.js, Tailwind, or complex external front-end frameworks).

---

## 🌟 Key Features

### 🛍️ Storefront & Product Management
- **Catalog & Collections**: Active products organized into clean categories with real-time stock counters.
- **Product Details**: High-resolution image showcase, unit pricing, real-time stock status badges (`In Stock`, `Low Stock`, `Out of Stock`), detailed specifications, and related category products.
- **Search & Filters**: Instant full-text search across product titles and descriptions, category sidebar filtering, and dynamic sorting (Newest, Price Low-to-High, Price High-to-Low, Alphabetical).
- **Pagination**: Server-side pagination with query-parameter retention across pages.
- **Storefront Privacy**: Strictly displays only active (`is_active=True`) products on the public storefront.

### 🛒 Shopping Cart
- **Session-Backed**: Stored securely in Django user sessions with no trust placed on client-submitted prices.
- **Interactive Controls**: Instant quantity adjustment (+ / - stepper buttons) and item removal.
- **Stock Guard**: Validates requested quantities against real-time database stock to prevent over-ordering.
- **Dynamic Badge**: Live cart count badge in the navigation bar via custom context processor.
- **Empty States**: Engaging, helpful empty cart interface guiding users to the catalog.

### 💳 Checkout & Atomic Order Processing
- **Authentication Protected**: Enforces user sign-in before checkout.
- **Real-Time Validation**: Server-side validation of customer name, phone number (digit format checks), address, city, and postal code.
- **Recalculated Prices**: All totals and line items are calculated strictly from the database records at checkout time.
- **ACID Database Transactions**: Uses `transaction.atomic()` with row-level locks (`select_for_update()`) to guarantee stock consistency.
- **Price & Name Snapshots**: Stores permanent snapshot data in `OrderItem` records so subsequent product edits or price changes do not distort historic order data.
- **Automatic Stock Decrement**: Safely deducts product stock only upon successful order commit.
- **Cash on Delivery (COD)**: Transparent Cash on Delivery payment option without pretending to charge dummy credit cards.
- **Cart Cleanup**: Automatically clears the session cart after order confirmation.

### 👤 Authentication & User Management
- **Django Auth System**: Secure user registration, login, and logout with PBKDF2 SHA-256 password hashing.
- **User Profile**: View and edit first name, last name, and email with duplicate email checks.
- **Strict Order Isolation**: Customers can only view their own orders; unauthorized attempts to access another user's order return a `404 Not Found`.
- **Order History**: Itemized order list with status pills (`Pending`, `Processing`, `Shipped`, `Delivered`, `Cancelled`).

### ⚙️ Django Admin Dashboard
- Manage categories, products, prices, stock levels, and active status.
- View customer orders with itemized inlines and customer shipping details.
- Update order statuses (`Pending` &rarr; `Processing` &rarr; `Shipped` &rarr; `Delivered` &rarr; `Cancelled`).
- Thumbnail previews and inline editing in product lists.

### 🎨 Modern UI & Responsive Design
- Clean, dark glassmorphic design system using CSS custom properties (variables).
- Responsive on mobile, tablet, and desktop screens.
- Accessible HTML5 semantics, labels, and image alt attributes.
- Custom 404 error page.

---

## 🗂️ Project Folder Structure

```
ecommerce-store/
│
├── manage.py                   # Django CLI management script
├── requirements.txt            # Project dependencies (Django, Pillow)
├── .gitignore                  # Git ignore rules for Python & Django
├── README.md                   # Complete documentation & setup instructions
├── db.sqlite3                  # Development SQLite database
│
├── config/                     # Project core configuration
│   ├── __init__.py
│   ├── settings.py             # Django settings, apps, templates, media config
│   ├── urls.py                 # Root URL routing and static/media handlers
│   ├── asgi.py                 # ASGI configuration
│   └── wsgi.py                 # WSGI configuration
│
├── store/                      # Main application
│   ├── __init__.py
│   ├── admin.py                # Admin configuration for all models
│   ├── apps.py                 # App registration
│   ├── models.py               # Category, Product, Order, OrderItem
│   ├── views.py                # Views for catalog, cart, auth, checkout, orders
│   ├── urls.py                 # URL patterns for store routes
│   ├── forms.py                # Registration, login, profile, checkout forms
│   ├── cart.py                 # Session cart class with DB stock validation
│   ├── context_processors.py   # Global cart counter and header categories
│   ├── tests.py                # Comprehensive test suite (22 tests)
│   ├── migrations/             # Database migrations
│   └── management/
│       └── commands/
│           └── seed_data.py    # Sample categories, products, images, and users
│
├── templates/                  # HTML templates
│   ├── base.html               # Base layout with navbar, alerts, footer
│   ├── store/
│   │   ├── home.html           # Landing page with hero, categories, featured products
│   │   ├── product_list.html   # Catalog with search, filters, and pagination
│   │   ├── product_detail.html # Product details with stock badge and add-to-cart
│   │   ├── cart.html           # Shopping cart review and quantity updates
│   │   ├── checkout.html       # Shipping form and payment selection
│   │   ├── order_confirmation.html # Receipt and success screen
│   │   ├── my_orders.html      # Customer order history list
│   │   ├── order_detail.html   # Detailed snapshot of a specific order
│   │   └── profile.html        # User account management & stats
│   ├── registration/
│   │   ├── login.html          # Login page
│   │   └── register.html       # Register page
│   └── errors/
│       └── 404.html            # Custom 404 page
│
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css           # Vanilla CSS design system
│   ├── js/
│   │   ├── main.js             # Mobile navigation, auto-dismissing alerts
│   │   └── cart.js             # Stepper controls and form submission
│   └── images/
│       └── logo.png            # Brand logo
│
└── media/                      # Uploaded / generated media
    └── products/               # Product showcase images
```

---

## 🚀 Quick Start Guide (Windows)

Follow these steps to set up and run the application locally:

### 1. Open Terminal & Navigate to Project Directory
Open PowerShell or Command Prompt:
```powershell
cd c:\Users\rsury\Downloads\E-commerce
```

### 2. Create and Activate Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Populate Sample Data (Categories, Products, Images & Accounts)
Run the built-in seeding command:
```powershell
python manage.py seed_data
```
This automatically:
- Creates **4 categories** (`Audio & Headphones`, `Smart Tech & Gadgets`, `Lifestyle & Apparel`, `Home & Workspace`).
- Generates **12 sample products** with high-resolution placeholder images in `media/products/`.
- Creates a default **administrator account**: `admin` / `admin123`.
- Creates a default **demo customer account**: `demouser` / `demo123`.

*(Optional)* You can also create a new administrator interactively:
```powershell
python manage.py createsuperuser
```

### 6. Run the Development Server
```powershell
python manage.py runserver
```

---

## 🌐 Accessing the Application

Once the development server is running, open your web browser:

- **Customer Storefront**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Django Admin Panel**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

### Default Credentials:
| Role | Username | Password |
|---|---|---|
| **Administrator** | `admin` | `admin123` |
| **Demo Customer** | `demouser` | `demo123` |

*(You can also register a new customer account anytime at [http://127.0.0.1:8000/register/](http://127.0.0.1:8000/register/))*

---

## 🧪 Running Automated Tests

A comprehensive test suite of **22 automated tests** verifies all core flows:
- User registration, login, logout, and profile updating
- Product listing, search, category filtering, and 404 on inactive products
- Adding, updating, and removing cart items
- Quantity boundaries and stock shortage enforcement
- Empty cart checkout prevention
- Atomic order placement with row-level locks
- Snapshot pricing and unit price persistence
- Stock reduction validation
- Strict order isolation (User A cannot view User B's orders)
- Custom 404 error page template rendering

To execute the test suite:
```powershell
python manage.py test
```

Expected output:
```text
Creating test database for alias 'default'...
Found 22 test(s).
System check identified no issues (0 silenced).
......................
----------------------------------------------------------------------
Ran 22 tests in ~30s

OK
Destroying test database for alias 'default'...
```

---

## 🛠️ Troubleshooting & Tips

### 1. "Pillow is not installed"
If image uploads fail, ensure Pillow is installed inside the virtual environment:
```powershell
pip install Pillow
```

### 2. Missing Images or Static Files
Ensure `DEBUG = True` in `config/settings.py` so Django automatically serves uploaded media from `media/` and static assets from `static/`.

### 3. Port 8000 Already in Use
If port 8000 is occupied by another process, specify another port:
```powershell
python manage.py runserver 8080
```
Then visit [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

### 4. Resetting the Database
If you ever want to start completely fresh:
```powershell
Remove-Item db.sqlite3
python manage.py migrate
python manage.py seed_data
```

---

## 📄 License
This project is open-source and intended for educational and commercial starter purposes.
#   C a r t N e s t - A - E - c o m m e r c e - W e b s i t e -  
 