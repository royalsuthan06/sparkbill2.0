from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, Product, Sale, SaleItem
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend')
CORS(app)

# Database configuration
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'arun_crackers_pos')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


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
            'description': p.description,
            'price': float(p.price),
            'cost_price': float(p.cost_price),
            'mrp': float(p.mrp),
            'stock_quantity': p.stock_quantity,
            'category': p.category
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
        'description': product.description,
        'price': float(product.price),
        'cost_price': float(product.cost_price),
        'mrp': float(product.mrp),
        'stock_quantity': product.stock_quantity,
        'category': product.category
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
        new_product = Product(
            sku=data['sku'],
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            cost_price=float(data.get('cost_price', 0)),
            mrp=float(data['mrp']),
            stock_quantity=int(data.get('stock_quantity', 0)),
            category=data.get('category', '')
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
        product.sku = data.get('sku', product.sku)
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = float(data.get('price', product.price))
        product.cost_price = float(data.get('cost_price', product.cost_price))
        product.mrp = float(data.get('mrp', product.mrp))
        product.stock_quantity = int(data.get('stock_quantity', product.stock_quantity))
        product.category = data.get('category', product.category)
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
            'customer_name': s.customer_name,
            'customer_mobile': s.customer_mobile,
            'total_amount': float(s.total_amount),
            'discount': float(s.discount),
            'amount_paid': float(s.amount_paid),
            'balance': float(s.balance),
            'payment_method': s.payment_method,
            'sale_date': s.sale_date.isoformat(),
            'items': len(s.items)
        } for s in sales
    ])


@app.route('/api/sales', methods=['POST'])
def create_sale():
    data = request.get_json()
    invoice_number = f'INV-{datetime.now().strftime("%Y%m%d%H%M%S")}'
    new_sale = Sale(
        invoice_number=invoice_number,
        customer_name=data.get('customer_name', ''),
        customer_mobile=data.get('customer_mobile', ''),
        total_amount=data['total_amount'],
        discount=data.get('discount', 0),
        amount_paid=data['amount_paid'],
        balance=data.get('balance', 0),
        payment_method=data.get('payment_method', 'Cash'),
        sale_date=datetime.utcnow()
    )
    db.session.add(new_sale)

    for item in data['items']:
        sale_item = SaleItem(
            sale=new_sale,
            product_id=item['product_id'],
            product_name=item['product_name'],
            quantity=item['quantity'],
            price=item['price'],
            mrp=item['mrp'],
            total=item['total']
        )
        db.session.add(sale_item)

        # Update product stock
        product = Product.query.get(item['product_id'])
        if product:
            product.stock_quantity -= item['quantity']

    db.session.commit()
    return jsonify({'id': new_sale.id, 'invoice_number': invoice_number}), 201


@app.route('/api/sales/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    items = [
        {
            'id': i.id,
            'product_id': i.product_id,
            'product_name': i.product_name,
            'quantity': i.quantity,
            'price': float(i.price),
            'mrp': float(i.mrp),
            'total': float(i.total)
        } for i in sale.items
    ]
    return jsonify({
        'id': sale.id,
        'invoice_number': sale.invoice_number,
        'customer_name': sale.customer_name,
        'customer_mobile': sale.customer_mobile,
        'total_amount': float(sale.total_amount),
        'discount': float(sale.discount),
        'amount_paid': float(sale.amount_paid),
        'balance': float(sale.balance),
        'payment_method': sale.payment_method,
        'sale_date': sale.sale_date.isoformat(),
        'items': items
    })


# Dashboard Stats Route
@app.route('/api/stats', methods=['GET'])
def get_stats():
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
    
    return jsonify({
        'today_sales': round(today_total, 2),
        'today_count': today_count,
        'total_skus': total_skus,
        'low_stock_items': low_stock,
        'inventory_value': round(inventory_value, 2)
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
