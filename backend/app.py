from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, Product, Sale, SaleItem
from datetime import datetime
import os
<<<<<<< HEAD
import webbrowser
import threading
=======
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend')
CORS(app)

<<<<<<< HEAD
basedir = os.path.abspath(os.path.dirname(__file__))

# Database configuration logic with fallback
DB_TYPE = os.getenv('DB_TYPE', '').lower()
=======
# Database configuration
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'arun_crackers_pos')
<<<<<<< HEAD

import socket

def is_mysql_running(host='localhost', port=3306):
    """Fast check if MySQL port is open."""
    try:
        with socket.create_connection((host, port), timeout=0.3):
            return True
    except Exception:
        return False

db_uri = None
if DB_TYPE == 'sqlite':
    db_path = os.path.abspath(os.path.join(basedir, '..', 'database', 'arun_crackers_pos.db'))
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_uri = f'sqlite:///{db_path}'
elif DB_TYPE == 'mysql':
    db_uri = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
else:
    # Auto-detect: Fast port check first, then verify credentials if open
    if is_mysql_running(DB_HOST) and DB_PASSWORD != 'your_password_here':
        try:
            import pymysql
            conn = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                connect_timeout=1
            )
            conn.close()
            db_uri = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
            print(f"[Database] Connected to MySQL database server at {DB_HOST}")
        except Exception as err:
            db_path = os.path.abspath(os.path.join(basedir, '..', 'database', 'arun_crackers_pos.db'))
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            db_uri = f'sqlite:///{db_path}'
            print(f"[Database] MySQL not accessible ({err}). Using SQLite database at: {db_path}")
    else:
        db_path = os.path.abspath(os.path.join(basedir, '..', 'database', 'arun_crackers_pos.db'))
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        db_uri = f'sqlite:///{db_path}'
        print(f"[Database] Using SQLite database at: {db_path}")

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
=======
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


<<<<<<< HEAD
import json

def seed_sample_data():
    """Seed sample data from inventory_data.json if Product table is empty."""
    if Product.query.first() is None:
        json_path = os.path.abspath(os.path.join(basedir, '..', 'database', 'inventory_data.json'))
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                items_data = json.load(f)
            sample_products = [
                Product(
                    sku=str(item['sku']),
                    name=str(item['name']),
                    description=str(item.get('description', '')),
                    price=float(item['price']),
                    cost_price=float(item.get('cost_price', 0)),
                    mrp=float(item['mrp']),
                    stock_quantity=int(item.get('stock_quantity', 100)),
                    category=str(item.get('category', 'General'))
                ) for item in items_data
            ]
            db.session.bulk_save_objects(sample_products)
            db.session.commit()
            print(f"[Database] Successfully seeded {len(sample_products)} products from PDF inventory.")
        else:
            sample_products = [
                Product(sku='001', name='Flower Pot - Special Large', description='Large flower pot crackers', price=250.00, cost_price=180.00, mrp=300.00, stock_quantity=50, category='Flower Pots'),
                Product(sku='002', name='Laxmi Bombs (28 Pcs)', description='Pack of 28 laxmi bombs', price=180.00, cost_price=120.00, mrp=180.00, stock_quantity=100, category='Sound Crackers'),
                Product(sku='003', name='Sparklers - Multicolour 15cm', description='Multicolour sparklers, 15cm', price=45.00, cost_price=25.00, mrp=45.00, stock_quantity=500, category='Sparklers'),
                Product(sku='004', name='Chakra - 5 Inch', description='5 inch chakra ground spinner', price=60.00, cost_price=40.00, mrp=75.00, stock_quantity=150, category='Visual Effects'),
                Product(sku='005', name='Rockets - 10 Pcs', description='Pack of 10 sky rockets', price=120.00, cost_price=80.00, mrp=150.00, stock_quantity=80, category='Rocket'),
            ]
            db.session.bulk_save_objects(sample_products)
            db.session.commit()
            print("[Database] Sample products seeded successfully.")



=======
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')


# Products Routes
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([
        {
            'id': p.id,
            'sku': p.sku,
            'name': p.name,
<<<<<<< HEAD
            'description': p.description or '',
            'price': float(p.price) if p.price is not None else 0.0,
            'cost_price': float(p.cost_price) if p.cost_price is not None else 0.0,
            'mrp': float(p.mrp) if p.mrp is not None else 0.0,
            'stock_quantity': p.stock_quantity or 0,
            'category': p.category or ''
=======
            'description': p.description,
            'price': float(p.price),
            'cost_price': float(p.cost_price),
            'mrp': float(p.mrp),
            'stock_quantity': p.stock_quantity,
            'category': p.category
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
        } for p in products
    ])


@app.route('/api/products/<sku>', methods=['GET'])
def get_product_by_sku(sku):
    product = Product.query.filter_by(sku=sku).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({
        'id': product.id,
        'sku': product.sku,
        'name': product.name,
<<<<<<< HEAD
        'description': product.description or '',
        'price': float(product.price) if product.price is not None else 0.0,
        'cost_price': float(product.cost_price) if product.cost_price is not None else 0.0,
        'mrp': float(product.mrp) if product.mrp is not None else 0.0,
        'stock_quantity': product.stock_quantity or 0,
        'category': product.category or ''
=======
        'description': product.description,
        'price': float(product.price),
        'cost_price': float(product.cost_price),
        'mrp': float(product.mrp),
        'stock_quantity': product.stock_quantity,
        'category': product.category
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
    })


@app.route('/api/products', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        required_fields = ['sku', 'name', 'price', 'mrp']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check for duplicate SKU
        existing_product = Product.query.filter_by(sku=data['sku']).first()
        if existing_product:
<<<<<<< HEAD
            return jsonify({'error': 'A product with this SKU already exists!'}), 400
        
        new_product = Product(
            sku=str(data['sku']),
            name=str(data['name']),
            description=str(data.get('description', '')),
=======
            return jsonify({'error': 'A product with this SKU already exists!'}),400
        
        new_product = Product(
            sku=data['sku'],
            name=data['name'],
            description=data.get('description', ''),
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
            price=float(data['price']),
            cost_price=float(data.get('cost_price', 0)),
            mrp=float(data['mrp']),
            stock_quantity=int(data.get('stock_quantity', 0)),
<<<<<<< HEAD
            category=str(data.get('category', ''))
=======
            category=data.get('category', '')
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'id': new_product.id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error adding product: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.get_json()
        product = Product.query.get_or_404(product_id)
        
        # Check for duplicate SKU (if changing SKU)
        if 'sku' in data and data['sku'] != product.sku:
            existing_product = Product.query.filter_by(sku=data['sku']).first()
            if existing_product:
<<<<<<< HEAD
                return jsonify({'error': 'A product with this SKU already exists!'}), 400
        
        product.sku = str(data.get('sku', product.sku))
        product.name = str(data.get('name', product.name))
        product.description = str(data.get('description', product.description))
=======
                return jsonify({'error': 'A product with this SKU already exists!'}),400
        
        product.sku = data.get('sku', product.sku)
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
        product.price = float(data.get('price', product.price))
        product.cost_price = float(data.get('cost_price', product.cost_price))
        product.mrp = float(data.get('mrp', product.mrp))
        product.stock_quantity = int(data.get('stock_quantity', product.stock_quantity))
<<<<<<< HEAD
        product.category = str(data.get('category', product.category))
=======
        product.category = data.get('category', product.category)
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
        db.session.commit()
        return jsonify({'message': 'Product updated successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Error updating product: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})


# Sales Routes
@app.route('/api/sales', methods=['GET'])
def get_sales():
    sales = Sale.query.order_by(Sale.sale_date.desc()).all()
    return jsonify([
        {
            'id': s.id,
            'invoice_number': s.invoice_number,
<<<<<<< HEAD
            'customer_name': s.customer_name or '',
            'customer_mobile': s.customer_mobile or '',
            'total_amount': float(s.total_amount) if s.total_amount is not None else 0.0,
            'discount': float(s.discount) if s.discount is not None else 0.0,
            'amount_paid': float(s.amount_paid) if s.amount_paid is not None else 0.0,
            'balance': float(s.balance) if s.balance is not None else 0.0,
            'payment_method': s.payment_method or 'Cash',
            'sale_date': s.sale_date.isoformat() if s.sale_date else datetime.now().isoformat(),
=======
            'customer_name': s.customer_name,
            'customer_mobile': s.customer_mobile,
            'total_amount': float(s.total_amount),
            'discount': float(s.discount),
            'amount_paid': float(s.amount_paid),
            'balance': float(s.balance),
            'payment_method': s.payment_method,
            'sale_date': s.sale_date.isoformat(),
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
            'items': len(s.items)
        } for s in sales
    ])


@app.route('/api/sales', methods=['POST'])
def create_sale():
    try:
        data = request.get_json()
        if not data or 'items' not in data or len(data['items']) == 0:
            return jsonify({'error': 'No items in sale'}), 400

        invoice_number = f'INV-{datetime.now().strftime("%Y%m%d%H%M%S")}'
        
<<<<<<< HEAD
        calculated_total = sum(float(item['price']) * int(item['quantity']) for item in data['items'])
        if abs(calculated_total - float(data.get('total_amount', 0))) > 0.01:
            return jsonify({'error': 'Total amount mismatch'}), 400
        
        if float(data.get('amount_paid', 0)) < 0:
            return jsonify({'error': 'Amount paid cannot be negative'}), 400

        product_ids = [item['product_id'] for item in data['items']]
        query = Product.query.filter(Product.id.in_(product_ids))
        if 'sqlite' not in app.config['SQLALCHEMY_DATABASE_URI']:
            products = query.with_for_update().all()
        else:
            products = query.all()

=======
        calculated_total = sum(item['price'] * item['quantity'] for item in data['items'])
        if abs(calculated_total - data.get('total_amount', 0)) > 0.01:
            return jsonify({'error': 'Total amount mismatch'}), 400
        
        if data.get('amount_paid', 0) < 0:
            return jsonify({'error': 'Amount paid cannot be negative'}), 400

        product_ids = [item['product_id'] for item in data['items']]
        products = Product.query.filter(Product.id.in_(product_ids)).with_for_update().all()
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
        product_map = {p.id: p for p in products}

        for item in data['items']:
            product = product_map.get(item['product_id'])
            if not product:
<<<<<<< HEAD
                return jsonify({'error': f"Product {item.get('product_name', '')} not found!"}), 400

            if product.stock_quantity < int(item['quantity']):
                return jsonify({
                    'error': f"Not enough stock for {product.name}! Only {product.stock_quantity} left in stock!"
=======
                return jsonify({'error': f"Product {item['product_name']} not found!"}), 400

            if product.stock_quantity < item['quantity']:
                return jsonify({
                    'error': f"Not enough stock for {item['product_name']}! Only {product.stock_quantity} left in stock!"
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
                }), 400

        new_sale = Sale(
            invoice_number=invoice_number,
            customer_name=data.get('customer_name', ''),
            customer_mobile=data.get('customer_mobile', ''),
            total_amount=data['total_amount'],
            discount=data.get('discount', 0),
            amount_paid=data['amount_paid'],
            balance=data.get('balance', 0),
            payment_method=data.get('payment_method', 'Cash'),
<<<<<<< HEAD
            sale_date=datetime.now()
=======
            sale_date=datetime.utcnow()
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
        )
        db.session.add(new_sale)

        for item in data['items']:
            sale_item = SaleItem(
                sale=new_sale,
                product_id=item['product_id'],
                product_name=item['product_name'],
<<<<<<< HEAD
                quantity=int(item['quantity']),
                price=float(item['price']),
                mrp=float(item['mrp']),
                total=float(item['price']) * int(item['quantity'])
=======
                quantity=item['quantity'],
                price=item['price'],
                mrp=item['mrp'],
                total=item['price'] * item['quantity']
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
            )
            db.session.add(sale_item)

            product = product_map[item['product_id']]
<<<<<<< HEAD
            product.stock_quantity -= int(item['quantity'])
=======
            product.stock_quantity -= item['quantity']
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a

        db.session.commit()
        return jsonify({'id': new_sale.id, 'invoice_number': invoice_number}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating sale: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/sales/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    items = [
        {
            'id': i.id,
            'product_id': i.product_id,
            'product_name': i.product_name,
            'quantity': i.quantity,
<<<<<<< HEAD
            'price': float(i.price) if i.price is not None else 0.0,
            'mrp': float(i.mrp) if i.mrp is not None else 0.0,
            'total': float(i.total) if i.total is not None else 0.0
=======
            'price': float(i.price),
            'mrp': float(i.mrp),
            'total': float(i.total)
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
        } for i in sale.items
    ]
    return jsonify({
        'id': sale.id,
        'invoice_number': sale.invoice_number,
<<<<<<< HEAD
        'customer_name': sale.customer_name or '',
        'customer_mobile': sale.customer_mobile or '',
        'total_amount': float(sale.total_amount) if sale.total_amount is not None else 0.0,
        'discount': float(sale.discount) if sale.discount is not None else 0.0,
        'amount_paid': float(sale.amount_paid) if sale.amount_paid is not None else 0.0,
        'balance': float(sale.balance) if sale.balance is not None else 0.0,
        'payment_method': sale.payment_method or 'Cash',
        'sale_date': sale.sale_date.isoformat() if sale.sale_date else datetime.now().isoformat(),
=======
        'customer_name': sale.customer_name,
        'customer_mobile': sale.customer_mobile,
        'total_amount': float(sale.total_amount),
        'discount': float(sale.discount),
        'amount_paid': float(sale.amount_paid),
        'balance': float(sale.balance),
        'payment_method': sale.payment_method,
        'sale_date': sale.sale_date.isoformat(),
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
        'items': items
    })


# Dashboard Stats Route
@app.route('/api/stats', methods=['GET'])
def get_stats():
<<<<<<< HEAD
    today = datetime.now().date()
    start_of_today = datetime.combine(today, datetime.min.time())
    today_sales = Sale.query.filter(Sale.sale_date >= start_of_today).all()
    today_total = sum(float(s.total_amount) for s in today_sales if s.total_amount is not None)
    today_count = len(today_sales)
    
    total_skus = Product.query.count()
    low_stock = Product.query.filter(Product.stock_quantity < 30).count()
    
    products = Product.query.all()
    inventory_value = sum((float(p.price) if p.price is not None else 0.0) * (p.stock_quantity or 0) for p in products)
=======
    # Get today's sales
    today = datetime.utcnow().date()
    today_sales = Sale.query.filter(db.func.date(Sale.sale_date) == today).all()
    today_total = sum(float(s.total_amount) for s in today_sales)
    today_count = len(today_sales)
    
    # Get total SKUs
    total_skus = Product.query.count()
    
    # Get low stock items (<30)
    low_stock = Product.query.filter(Product.stock_quantity < 30).count()
    
    # Get inventory value
    products = Product.query.all()
    inventory_value = sum(float(p.price) * p.stock_quantity for p in products)
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
    
    return jsonify({
        'today_sales': round(today_total, 2),
        'today_count': today_count,
        'total_skus': total_skus,
        'low_stock_items': low_stock,
        'inventory_value': round(inventory_value, 2)
    })


<<<<<<< HEAD
def init_db():
    with app.app_context():
        db.create_all()
        seed_sample_data()


def start_app():
    init_db()
    # Only open the browser in the main process, not in the Werkzeug reloader child
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        threading.Timer(1.2, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    print("=" * 60)
    print(" SparkBill POS App is running at http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, port=5000)


if __name__ == '__main__':
    start_app()

=======
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
>>>>>>> e52a7f2fda1925932fd783d6ed5c998a279a268a
