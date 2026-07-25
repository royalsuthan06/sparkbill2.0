import os
import sys

# Locate and configure Python DLL for pythonnet/clr_loader in frozen environments
if getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(sys.executable)
    search_dirs = [
        os.path.join(exe_dir, '_internal'),
        exe_dir
    ]
    if hasattr(sys, '_MEIPASS'):
        search_dirs.insert(0, os.path.join(sys._MEIPASS, '_internal'))
        search_dirs.insert(0, sys._MEIPASS)
        
    py_dll = None
    for d in search_dirs:
        if os.path.exists(d):
            # Add to PATH so that clr_loader/Windows can find python3xx.dll and other dependency DLLs
            if d not in os.environ['PATH']:
                os.environ['PATH'] = d + os.pathsep + os.environ['PATH']
            
            for file in os.listdir(d):
                if file.lower().startswith('python3') and file.lower().endswith('.dll'):
                    py_dll = os.path.abspath(os.path.join(d, file))
                    break
    if py_dll:
        os.environ['PYTHONNET_PYDLL'] = py_dll

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, Product, Sale, SaleItem
from datetime import datetime
import threading
import webview
from dotenv import load_dotenv


# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Load environment variables
load_dotenv()

# Define BASE_DIR
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    bundle_dir = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bundle_dir = BASE_DIR

static_folder = os.path.join(bundle_dir, 'frontend', 'static')
template_folder = os.path.join(bundle_dir, 'frontend')

app = Flask(__name__, static_folder=static_folder, template_folder=template_folder)
CORS(app)

# Ensure database directory exists next to exe or in project root
DB_FOLDER = os.path.join(BASE_DIR, 'database')
os.makedirs(DB_FOLDER, exist_ok=True)
db_path = os.path.abspath(os.path.join(DB_FOLDER, 'arun_crackers_pos.db'))
db_uri = f'sqlite:///{db_path}'

print(f"[Database] Using SQLite database at: {db_path}")

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


import json

def seed_sample_data():
    """Seed sample data from inventory_data.json, adding any missing products."""
    # Check bundled path first, then fallback to BASE_DIR path
    if getattr(sys, 'frozen', False):
        json_path = os.path.join(sys._MEIPASS, 'database', 'inventory_data.json')
        if not os.path.exists(json_path):
            json_path = os.path.join(BASE_DIR, 'database', 'inventory_data.json')
    else:
        json_path = os.path.join(BASE_DIR, 'database', 'inventory_data.json')

    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            items_data = json.load(f)
        
        # Get existing SKUs from the database
        existing_products = Product.query.with_entities(Product.sku).all()
        existing_skus = {p.sku for p in existing_products}
        
        new_products = []
        for item in items_data:
            if str(item['sku']) not in existing_skus:
                new_products.append(Product(
                    sku=str(item['sku']),
                    name=str(item['name']),
                    description=str(item.get('description', '')),
                    price=float(item['price']),
                    stock_quantity=int(item.get('stock_quantity', 100)),
                    category=str(item.get('category', 'General'))
                ))
                
        if new_products:
            db.session.bulk_save_objects(new_products)
            db.session.commit()
            print(f"[Database] Successfully seeded {len(new_products)} new products from inventory data.")
    else:
        # Fallback if json doesn't exist and DB is empty
        if Product.query.first() is None:
            sample_products = [
                Product(sku='001', name='Flower Pot - Special Large', description='Large flower pot crackers', price=250.00, stock_quantity=50, category='Flower Pots'),
                Product(sku='002', name='Laxmi Bombs (28 Pcs)', description='Pack of 28 laxmi bombs', price=180.00, stock_quantity=100, category='Sound Crackers'),
                Product(sku='003', name='Sparklers - Multicolour 15cm', description='Multicolour sparklers, 15cm', price=45.00, stock_quantity=500, category='Sparklers'),
                Product(sku='004', name='Chakra - 5 Inch', description='5 inch chakra ground spinner', price=60.00, stock_quantity=150, category='Visual Effects'),
                Product(sku='005', name='Rockets - 10 Pcs', description='Pack of 10 sky rockets', price=120.00, stock_quantity=80, category='Rocket'),
            ]
            db.session.bulk_save_objects(sample_products)
            db.session.commit()
            print("[Database] Sample products seeded successfully.")



@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')


# Products Routes
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([
        {
            'id': p.id,
            'sku': p.sku,
            'name': p.name,
            'description': p.description or '',
            'price': float(p.price) if p.price is not None else 0.0,
            'stock_quantity': p.stock_quantity or 0,
            'category': p.category or ''
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
        'description': product.description or '',
        'price': float(product.price) if product.price is not None else 0.0,
        'stock_quantity': product.stock_quantity or 0,
        'category': product.category or ''
    })


@app.route('/api/products', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        required_fields = ['sku', 'name', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check for duplicate SKU
        existing_product = Product.query.filter_by(sku=data['sku']).first()
        if existing_product:
            return jsonify({'error': 'A product with this SKU already exists!'}), 400
        
        new_product = Product(
            sku=str(data['sku']),
            name=str(data['name']),
            description=str(data.get('description', '')),
            price=float(data['price']),
            stock_quantity=int(data.get('stock_quantity', 0)),
            category=str(data.get('category', ''))
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
                return jsonify({'error': 'A product with this SKU already exists!'}), 400
        
        product.sku = str(data.get('sku', product.sku))
        product.name = str(data.get('name', product.name))
        product.description = str(data.get('description', product.description))
        product.price = float(data.get('price', product.price))
        product.stock_quantity = int(data.get('stock_quantity', product.stock_quantity))
        product.category = str(data.get('category', product.category))
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
            'customer_name': s.customer_name or '',
            'customer_mobile': s.customer_mobile or '',
            'total_amount': float(s.total_amount) if s.total_amount is not None else 0.0,
            'discount': float(s.discount) if s.discount is not None else 0.0,
            'amount_paid': float(s.amount_paid) if s.amount_paid is not None else 0.0,
            'balance': float(s.balance) if s.balance is not None else 0.0,
            'payment_method': s.payment_method or 'Cash',
            'sale_date': s.sale_date.isoformat() if s.sale_date else datetime.now().isoformat(),
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

        product_map = {p.id: p for p in products}

        for item in data['items']:
            product = product_map.get(item['product_id'])
            if not product:
                return jsonify({'error': f"Product {item.get('product_name', '')} not found!"}), 400

        new_sale = Sale(
            invoice_number=invoice_number,
            customer_name=data.get('customer_name', ''),
            customer_mobile=data.get('customer_mobile', ''),
            total_amount=data['total_amount'],
            discount=data.get('discount', 0),
            amount_paid=data['amount_paid'],
            balance=data.get('balance', 0),
            payment_method=data.get('payment_method', 'Cash'),
            sale_date=datetime.now()
        )
        db.session.add(new_sale)

        for item in data['items']:
            sale_item = SaleItem(
                sale=new_sale,
                product_id=item['product_id'],
                product_name=item['product_name'],
                quantity=int(item['quantity']),
                price=float(item['price']),
                total=float(item['price']) * int(item['quantity'])
            )
            db.session.add(sale_item)

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
            'price': float(i.price) if i.price is not None else 0.0,
            'total': float(i.total) if i.total is not None else 0.0
        } for i in sale.items
    ]
    return jsonify({
        'id': sale.id,
        'invoice_number': sale.invoice_number,
        'customer_name': sale.customer_name or '',
        'customer_mobile': sale.customer_mobile or '',
        'total_amount': float(sale.total_amount) if sale.total_amount is not None else 0.0,
        'discount': float(sale.discount) if sale.discount is not None else 0.0,
        'amount_paid': float(sale.amount_paid) if sale.amount_paid is not None else 0.0,
        'balance': float(sale.balance) if sale.balance is not None else 0.0,
        'payment_method': sale.payment_method or 'Cash',
        'sale_date': sale.sale_date.isoformat() if sale.sale_date else datetime.now().isoformat(),
        'items': items
    })


# Dashboard Stats Route
@app.route('/api/stats', methods=['GET'])
def get_stats():
    today = datetime.now().date()
    start_of_today = datetime.combine(today, datetime.min.time())
    today_sales = Sale.query.filter(Sale.sale_date >= start_of_today).all()
    today_total = sum(float(s.total_amount) for s in today_sales if s.total_amount is not None)
    today_count = len(today_sales)
    
    total_skus = Product.query.count()
    
    return jsonify({
        'today_sales': round(today_total, 2),
        'today_count': today_count,
        'total_skus': total_skus,
        'low_stock_items': 0,
        'inventory_value': 0.0
    })


def generate_invoice_pdf(sale):
    invoices_dir = os.path.join(BASE_DIR, 'invoices')
    os.makedirs(invoices_dir, exist_ok=True)
    pdf_path = os.path.join(invoices_dir, f"{sale.invoice_number}.pdf")
    
    # Page setup - A4
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    # Primary theme colors - Deep warm Red for crackers and elegant styling
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=28,
        textColor=colors.HexColor('#cc1100'),
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'InvoiceSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=12,
        textColor=colors.HexColor('#555555'),
        spaceAfter=15
    )
    
    info_header_style = ParagraphStyle(
        'InfoHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#333333'),
    )
    
    info_val_style = ParagraphStyle(
        'InfoVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#333333'),
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.white,
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#333333'),
    )
    
    table_cell_right_style = ParagraphStyle(
        'TableCellRight',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        alignment=2, # Right aligned
        textColor=colors.HexColor('#333333'),
    )

    table_header_right_style = ParagraphStyle(
        'TableHeaderRight',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        alignment=2, # Right aligned
        textColor=colors.white,
    )
    
    footer_style = ParagraphStyle(
        'InvoiceFooter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#777777'),
        alignment=1, # Center
        spaceBefore=20
    )
    
    # Invoice Header Banner
    story.append(Paragraph("Arun Crackers", title_style))
    story.append(Paragraph("Ignite POS - Premium Point of Sale", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Customer and Invoice Info Grid
    date_str = sale.sale_date.strftime("%d-%m-%Y %I:%M %p") if sale.sale_date else datetime.now().strftime("%d-%m-%Y %I:%M %p")
    
    info_data = [
        [Paragraph("Invoice Number:", info_header_style), Paragraph(sale.invoice_number, info_val_style),
         Paragraph("Date & Time:", info_header_style), Paragraph(date_str, info_val_style)],
        [Paragraph("Customer Name:", info_header_style), Paragraph(sale.customer_name or "Walk-in", info_val_style),
         Paragraph("Payment Method:", info_header_style), Paragraph(sale.payment_method or "Cash", info_val_style)],
        [Paragraph("Customer Mobile:", info_header_style), Paragraph(sale.customer_mobile or "N/A", info_val_style),
         Paragraph("", info_header_style), Paragraph("", info_val_style)]
    ]
    
    info_table = Table(info_data, colWidths=[110, 150, 110, 150])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Items Table
    # Table headers: SNo, Item Name, Price, Qty, Total
    table_data = [
        [
            Paragraph("S.No", table_header_style),
            Paragraph("Item Name", table_header_style),
            Paragraph("Price", table_header_right_style),
            Paragraph("Quantity", table_header_right_style),
            Paragraph("Total", table_header_right_style),
        ]
    ]
    
    sno = 1
    for item in sale.items:
        table_data.append([
            Paragraph(str(sno), table_cell_style),
            Paragraph(item.product_name, table_cell_style),
            Paragraph(f"INR {float(item.price):.2f}", table_cell_right_style),
            Paragraph(str(item.quantity), table_cell_right_style),
            Paragraph(f"INR {float(item.total):.2f}", table_cell_right_style),
        ])
        sno += 1
        
    items_table = Table(table_data, colWidths=[40, 240, 80, 70, 90])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#cc1100')), # Crimson header
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fbfbfb')]), # Zebra patterning
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 15))
    
    # Totals Section
    total_data = [
        [Paragraph("", info_header_style), Paragraph("Total Amount:", info_header_style), Paragraph(f"INR {float(sale.total_amount):.2f}", info_header_style)],
        [Paragraph("", info_header_style), Paragraph("Amount Paid:", info_header_style), Paragraph(f"INR {float(sale.amount_paid):.2f}", info_header_style)],
        [Paragraph("", info_header_style), Paragraph("Balance:", info_header_style), Paragraph(f"INR {float(sale.balance):.2f}", info_header_style)]
    ]
    total_table = Table(total_data, colWidths=[280, 120, 120])
    total_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    
    story.append(total_table)
    story.append(Spacer(1, 30))
    
    # Footer
    story.append(Paragraph("Thank you for your business! We wish you a safe and sparky celebration!", footer_style))
    story.append(Paragraph("This is a computer-generated invoice and does not require a physical signature.", footer_style))
    
    doc.build(story)
    return pdf_path


@app.route('/api/sales/<int:sale_id>/print', methods=['GET'])
def print_sale_invoice(sale_id):
    try:
        sale = Sale.query.get_or_404(sale_id)
        pdf_path = generate_invoice_pdf(sale)
        
        # open the PDF file in OS default viewer
        if os.path.exists(pdf_path):
            if sys.platform == 'win32':
                os.startfile(pdf_path)
            elif sys.platform == 'darwin':
                import subprocess
                subprocess.Popen(['open', pdf_path])
            else:
                import subprocess
                subprocess.Popen(['xdg-open', pdf_path])
            return jsonify({'success': True, 'invoice_path': pdf_path}), 200
        else:
            return jsonify({'error': 'Invoice PDF file not found after generation'}), 500
    except Exception as e:
        print(f"Error printing sale invoice: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/sales/<int:sale_id>/pdf', methods=['GET'])
def download_sale_invoice_pdf(sale_id):
    try:
        sale = Sale.query.get_or_404(sale_id)
        pdf_path = generate_invoice_pdf(sale)
        directory = os.path.dirname(pdf_path)
        filename = os.path.basename(pdf_path)
        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        print(f"Error serving pdf: {e}")
        return jsonify({'error': str(e)}), 500


def init_db():
    with app.app_context():
        db.create_all()
        seed_sample_data()


def start_app():
    init_db()
    
    # Run Flask on 127.0.0.1:5000 in a background daemon thread
    flask_thread = threading.Thread(
        target=lambda: app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False),
        daemon=True
    )
    flask_thread.start()
    
    # Initialize pywebview desktop window
    print("=" * 60)
    print(" ArunCrackers POS App is running desktop window via pywebview...")
    print("=" * 60)
    webview.create_window("ArunCrackers", "http://127.0.0.1:5000", width=1280, height=800, resizable=True)
    webview.start()


if __name__ == '__main__':
    start_app()

