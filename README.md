# Arun Crackers POS System

A full-stack POS (Point of Sale) system for Arun Crackers, built with Flask backend, MySQL database, and HTML/CSS/JS frontend.

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS
- **Backend**: Flask (Python)
- **Database**: MySQL
- **ORM**: Flask-SQLAlchemy
- **CORS**: Flask-CORS

## Setup Instructions

### Prerequisites

1. Python 3.8+
2. MySQL Server
3. pip package manager

### 1. Clone or navigate to the project directory

```bash
cd "c:\Mini project\Arun Crackers\arun_crackers_pos_app"
```

### 2. Set up MySQL Database

- Start MySQL server
- Create a database (or use the schema.sql file):

```bash
mysql -u root -p
```

Then run:
```sql
source database/schema.sql;
```

Or you can manually create the database and tables:
```sql
CREATE DATABASE arun_crackers_pos;
USE arun_crackers_pos;
-- Then run the CREATE TABLE statements from database/schema.sql
```

### 3. Set up Python Virtual Environment (Optional but recommended)

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

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Database Connection

Copy the example .env file and update with your MySQL credentials:

```bash
cd backend
cp .env.example .env
```

Then edit the `.env` file to set your database username and password:
```env
# Database Configuration
DB_USER=root
DB_PASSWORD=your_actual_mysql_password
DB_HOST=localhost
DB_NAME=arun_crackers_pos
```

### 6. Run the Backend

```bash
cd backend
python app.py
```

The server will start at `http://localhost:5000`

### 7. Access the Application

Open your browser and go to `http://localhost:5000`

## Project Structure

```
arun_crackers_pos_app/
├── backend/
│   ├── app.py                 # Flask application with API routes
│   ├── models.py              # SQLAlchemy models
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Example environment variables
│   └── .env                   # Your actual environment variables (gitignored)
├── database/
│   └── schema.sql             # Database schema with sample data
├── frontend/
│   ├── index.html             # Main HTML file
│   └── static/
│       ├── css/
│       │   └── style.css      # Custom CSS (empty for now, using Tailwind)
│       └── js/
│           └── app.js         # Frontend JavaScript
├── .gitignore                 # Git ignore file
└── README.md                  # This file
```

## Features

- **Quick Billing**: Add products by SKU/Barcode
- **Inventory Management**: Add and view products
- **Sales Reports**: View all sales records
- **Hotkeys**:
  - F1: Focus SKU input
  - F2: Focus Quantity input
  - F3: Focus Customer Name
  - F8: Void last item
  - F12: Checkout & Print

## Default Sample Products

- SKU 001: Flower Pot - Special Large (₹250)
- SKU 002: Laxmi Bombs (28 Pcs) (₹180)
- SKU 003: Sparklers - Multicolour 15cm (₹45)
- SKU 004: Chakra - 5 Inch (₹60)
- SKU 005: Rockets - 10 Pcs (₹120)
