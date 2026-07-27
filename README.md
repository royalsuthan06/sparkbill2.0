# Arun Crackers POS System

A full-stack POS (Point of Sale) system for Arun Crackers, built with Flask backend, SQLite database, and HTML/CSS/JS frontend.

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript (vanilla), Tailwind CSS
- **Backend**: Flask (Python)
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
cd backend
python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
venv\Scripts\activate.bat
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Backend

```bash
cd backend
python app.py
```

The SQLite database is created automatically on first run at `database/arun_crackers_pos.db`. Sample products are seeded from `database/inventory_data.json`.

The server will start at `http://localhost:5000`

### 5. Access the Application

Open your browser and go to `http://localhost:5000`

### 6. Run Tests

```bash
cd backend
python -m pytest test_app.py -v
```

## Project Structure

```
SparkBill/
├── backend/
│   ├── app.py                 # Flask application with API routes
│   ├── models.py              # SQLAlchemy models
│   ├── test_app.py            # pytest tests
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables (gitignored)
├── database/
│   ├── schema.sql             # Database schema reference
│   └── inventory_data.json    # Product seed data (153 products)
├── frontend/
│   ├── index.html             # Main HTML file
│   └── static/
│       ├── css/
│       │   └── style.css      # Custom CSS
│       └── js/
│           ├── api.js         # API helpers, SKU lookup, toast notifications
│           ├── billing.js     # Cart management, checkout, payment
│           ├── inventory.js   # Product CRUD, filters
│           ├── reports.js     # Sales reports, PDF view, sale details
│           └── app.js         # Init, navigation, hotkeys, event wiring
├── .gitignore
└── README.md
```

## Features

- **Quick Billing**: Typeahead SKU search (matches SKU or product name), arrow-key cart navigation
- **Cart Keyboard Controls**: Delete key enters row-select mode, Arrow Up/Down to navigate, Enter to delete, Escape to exit
- **Inventory Management**: Add, edit, delete products with category and price filters
- **Sales Reports**: Filter by today/yesterday/7 days/custom date range, view sale details, reprint PDFs
- **PDF Invoices**: Auto-generated at sale time, cached for instant reprint
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
