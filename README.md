# SparkBill POS

A full-stack Point of Sale (POS) system for Arun Crackers, built with a Flask backend, SQLite database, and a vanilla HTML/CSS/JS frontend. It runs as a desktop window via pywebview (WebView2) and is also reachable in any browser.

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript (vanilla), Tailwind CSS (local offline copy)
- **Backend**: Flask (Python) served by waitress (WSGI)
- **Desktop Shell**: pywebview (Microsoft Edge WebView2)
- **Database**: SQLite (auto-created, no setup needed)
- **ORM**: Flask-SQLAlchemy
- **PDF**: ReportLab

## Setup Instructions

### Prerequisites

1. Python 3.8+
2. pip package manager

### 1. Clone or navigate to the project directory

```bash
cd "SparkBill"
```

### 2. Set up Python Virtual Environment (Optional but recommended)

```bash
python -m venv .venv
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.venv\Scripts\activate.bat
# On Linux/macOS:
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Run the App

From the project root:

```bash
python app.py
```

or double-click `run.bat`. You can also run it from inside the `backend/` folder:

```bash
cd backend
python app.py
```

On first run, the SQLite database is created automatically at `database/arun_crackers_pos.db` and seeded with 151 sample products from `database/inventory_data.json`.

The app opens a desktop window (SparkBill POS) via pywebview. The server also listens at `http://127.0.0.1:5000`, so you can open the same UI in any browser. If waitress is not installed, it falls back to the Flask dev server automatically.

### 5. Run Tests

```bash
cd backend
python -m pytest test_app.py -v
```

(22 tests covering billing, inventory, sales reports, validation, and security.)

## Project Structure

```
SparkBill/
├── app.py                   # Entry point (launcher)
├── flask_utils.py           # Frozen-path helper for packaged builds
├── run.bat                  # Windows launcher
├── build.bat                # PyInstaller build script
├── logo.ico                 # App icon
├── backend/
│   ├── app.py               # Flask application, API routes, CSP, seeding
│   ├── models.py            # SQLAlchemy models
│   ├── test_app.py          # pytest tests
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables (gitignored)
├── database/
│   ├── schema.sql           # Database schema reference
│   └── inventory_data.json  # Product seed data (151 products)
├── frontend/
│   ├── index.html           # Main HTML file (no inline scripts)
│   └── static/
│       ├── css/
│       │   ├── style.css              # Custom CSS
│       │   ├── fonts.css              # Local font faces
│       │   └── material-symbols.css   # Material Symbols icons
│       ├── fonts/                     # Bundled woff2 fonts (offline)
│       └── js/
│           ├── tailwindcss.js         # Tailwind Play CDN (offline copy)
│           ├── tailwind-config.js     # Tailwind theme config (external)
│           ├── api.js                 # API helpers, SKU lookup, toast notifications
│           ├── billing.js             # Cart management, checkout, payment
│           ├── inventory.js           # Product CRUD, filters
│           ├── reports.js             # Sales reports, PDF view, sale details
│           └── app.js                 # Init, navigation, hotkeys, event wiring
├── invoices/                # Generated PDF invoices
├── .gitignore
└── README.md
```

## Features

- **Quick Billing**: Typeahead SKU search (matches SKU or product name), arrow-key cart navigation
- **Cart Keyboard Controls**: Delete key enters row-select mode, Arrow Up/Down to navigate, Enter to delete, Escape to exit
- **Inventory Management**: Add, edit, delete products (with deletion guard) and category/price filters
- **Sales Reports**: Filter by today/yesterday/7 days/custom date range, view sale details, reprint PDFs, paginated sales listing
- **PDF Invoices**: Auto-generated at sale time with ReportLab, cached for instant reprint
- **Input Validation**: Mobile number format check (`^\+?[0-9]{7,15}$`) and overpayment rejected at checkout
- **Security**: Content Security Policy headers, secret key from environment, fully offline assets (no CDN calls)
- **Hotkeys**:
  - F1: Focus SKU input
  - F2: Focus Quantity input
  - F3: Focus Customer Name
  - F8: Void cart
  - F12: Checkout & Print

## Default Sample Products

- SKU 001: Flower Pot - Special Large (₹250)
- SKU 002: Laxmi Bombs (28 Pcs) (₹180)
- SKU 003: Sparklers - Multicolour 15cm (₹45)
- SKU 004: Chakra - 5 Inch (₹60)
- SKU 005: Rockets - 10 Pcs (₹120)
