import os
import sys
import secrets
import json
import re
import threading

from dotenv import load_dotenv
load_dotenv()

try:
    from flask_utils import configure_frozen_path
    configure_frozen_path()
except ImportError:
    pass

from flask import Flask, request, jsonify, send_from_directory, abort
from models import db, Product, Sale, SaleItem, InvoiceCounter
from datetime import datetime
import webview
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from xml.sax.saxutils import escape as xml_escape

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    bundle_dir = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bundle_dir = BASE_DIR

static_folder = os.path.join(bundle_dir, 'frontend', 'static')
template_folder = os.path.join(bundle_dir, 'frontend')

app = Flask(__name__, static_folder=static_folder, template_folder=template_folder)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

_invoice_lock = threading.Lock()

DB_FOLDER = os.path.join(BASE_DIR, 'database')
os.makedirs(DB_FOLDER, exist_ok=True)
db_path = os.path.abspath(os.path.join(DB_FOLDER, 'arun_crackers_pos.db'))
db_uri = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.after_request
def no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'"
    )
    return response


def seed_sample_data():
    if getattr(sys, 'frozen', False):
        json_path = os.path.join(sys._MEIPASS, 'database', 'inventory_data.json')
        if not os.path.exists(json_path):
            json_path = os.path.join(BASE_DIR, 'database', 'inventory_data.json')
    else:
        json_path = os.path.join(BASE_DIR, 'database', 'inventory_data.json')

    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            items_data = json.load(f)
        
        existing_products = Product.query.with_entities(Product.sku).all()
        existing_skus = {p.sku for p in existing_products}
        
        new_products = []
        for item in items_data:
            if str(item['sku']) not in existing_skus:
                new_products.append(Product(
                    sku=str(item['sku']),
                    name=str(item['name']),
                    price=float(item['price']),
                    category=str(item.get('category', 'General'))
                ))
                
        if new_products:
            db.session.add_all(new_products)
            db.session.commit()
            logger.info(f"Successfully seeded {len(new_products)} new products from inventory data.")
    else:
        if Product.query.first() is None:
            sample_products = [
                Product(sku='001', name='Flower Pot - Special Large', price=250.00, category='Flower Pots'),
                Product(sku='002', name='Laxmi Bombs (28 Pcs)', price=180.00, category='Sound Crackers'),
                Product(sku='003', name='Sparklers - Multicolour 15cm', price=45.00, category='Sparklers'),
                Product(sku='004', name='Chakra - 5 Inch', price=60.00, category='Visual Effects'),
                Product(sku='005', name='Rockets - 10 Pcs', price=120.00, category='Rocket'),
            ]
            db.session.add_all(sample_products)
            db.session.commit()
            logger.info("Sample products seeded successfully.")



@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')


@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([
        {
            'id': p.id,
            'sku': p.sku,
            'name': p.name,
            'price': float(p.price) if p.price is not None else 0.0,
            'category': p.category or ''
        } for p in products
    ])


@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = db.session.query(Product.category).distinct().filter(Product.category.isnot(None)).filter(Product.category != '').order_by(Product.category).all()
    return jsonify([c[0] for c in categories])


@app.route('/api/products/lookup/<sku>', methods=['GET'])
def get_product_by_sku(sku):
    product = Product.query.filter_by(sku=sku).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({
        'id': product.id,
        'sku': product.sku,
        'name': product.name,
        'price': float(product.price) if product.price is not None else 0.0,
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
        
        sku = str(data['sku']).strip()
        name = str(data['name']).strip()
        category = str(data.get('category', '')).strip()
        try:
            price = float(data['price'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Price must be a valid number'}), 400

        if not sku:
            return jsonify({'error': 'SKU cannot be empty'}), 400
        if not name:
            return jsonify({'error': 'Product name cannot be empty'}), 400
        if len(sku) > 50:
            return jsonify({'error': 'SKU must be 50 characters or fewer'}), 400
        if len(name) > 255:
            return jsonify({'error': 'Product name must be 255 characters or fewer'}), 400
        if len(category) > 100:
            return jsonify({'error': 'Category must be 100 characters or fewer'}), 400
        if price < 0:
            return jsonify({'error': 'Price cannot be negative'}), 400
        if price > 99999.99:
            return jsonify({'error': 'Price cannot exceed 99999.99'}), 400
        
        existing_product = Product.query.filter_by(sku=sku).first()
        if existing_product:
            return jsonify({'error': 'A product with this SKU already exists!'}), 400
        
        new_product = Product(
            sku=sku,
            name=name,
            price=price,
            category=category
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'id': new_product.id}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding product: {str(e)}")
        return jsonify({'error': 'Failed to add product'}), 500


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        if 'sku' in data:
            sku = str(data['sku']).strip()
            if len(sku) > 50:
                return jsonify({'error': 'SKU must be 50 characters or fewer'}), 400
            if sku != product.sku:
                existing_product = Product.query.filter_by(sku=sku).first()
                if existing_product:
                    return jsonify({'error': 'A product with this SKU already exists!'}), 400
            product.sku = sku
        
        if 'name' in data:
            name = str(data['name']).strip()
            if len(name) > 255:
                return jsonify({'error': 'Product name must be 255 characters or fewer'}), 400
            product.name = name
        
        if 'price' in data:
            try:
                price = float(data['price'])
            except (ValueError, TypeError):
                return jsonify({'error': 'Price must be a valid number'}), 400
            if price < 0:
                return jsonify({'error': 'Price cannot be negative'}), 400
            if price > 99999.99:
                return jsonify({'error': 'Price cannot exceed 99999.99'}), 400
            product.price = price
        
        if 'category' in data:
            category = str(data['category']).strip()
            if len(category) > 100:
                return jsonify({'error': 'Category must be 100 characters or fewer'}), 400
            product.category = category
        db.session.commit()
        return jsonify({'message': 'Product updated successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating product: {str(e)}")
        return jsonify({'error': 'Failed to update product'}), 500


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    try:
        existing_sales = SaleItem.query.filter_by(product_id=product_id).first()
        if existing_sales:
            return jsonify({'error': 'Cannot delete product: it has existing sales records'}), 400
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting product: {e}")
        return jsonify({'error': 'Failed to delete product'}), 500


@app.route('/api/sales', methods=['GET'])
def get_sales():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    per_page = min(per_page, 500)

    pagination = Sale.query.order_by(Sale.sale_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'sales': [
            {
                'id': s.id,
                'invoice_number': s.invoice_number,
                'customer_name': s.customer_name or '',
                'customer_mobile': s.customer_mobile or '',
                'total_amount': float(s.total_amount) if s.total_amount is not None else 0.0,
                'amount_paid': float(s.amount_paid) if s.amount_paid is not None else 0.0,
                'balance': float(s.balance) if s.balance is not None else 0.0,
                'payment_method': s.payment_method or 'Cash',
                'sale_date': s.sale_date.isoformat() if s.sale_date else datetime.now().isoformat(),
                'items': len(s.items)
            } for s in pagination.items
        ],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages
    })


@app.route('/api/sales', methods=['POST'])
def create_sale():
    try:
        data = request.get_json()
        if not data or 'items' not in data or len(data['items']) == 0:
            return jsonify({'error': 'No items in sale'}), 400

        if len(data['items']) > 100:
            return jsonify({'error': 'Sale cannot contain more than 100 items'}), 400

        customer_name = str(data.get('customer_name', '')).strip()
        customer_mobile = str(data.get('customer_mobile', '')).strip()
        payment_method = str(data.get('payment_method', 'Cash')).strip()
        if len(customer_name) > 255:
            return jsonify({'error': 'Customer name must be 255 characters or fewer'}), 400
        if len(customer_mobile) > 20:
            return jsonify({'error': 'Customer mobile must be 20 characters or fewer'}), 400
        valid_payment_methods = {'Cash', 'UPI', 'Card', 'Online'}
        if payment_method not in valid_payment_methods:
            return jsonify({'error': f'Invalid payment method. Allowed: {", ".join(sorted(valid_payment_methods))}'}), 400

        for item in data['items']:
            if 'product_id' not in item:
                return jsonify({'error': 'Each item must have a product_id'}), 400
            try:
                item['product_id'] = int(item['product_id'])
            except (ValueError, TypeError):
                return jsonify({'error': 'product_id must be a valid integer'}), 400
            try:
                qty = int(item.get('quantity', 0))
            except (ValueError, TypeError):
                return jsonify({'error': 'Quantity must be a valid integer'}), 400
            if qty <= 0:
                return jsonify({'error': 'Quantity must be greater than 0'}), 400
            if qty > 9999:
                return jsonify({'error': 'Quantity cannot exceed 9999'}), 400

        product_ids = [item['product_id'] for item in data['items']]
        products = Product.query.filter(Product.id.in_(product_ids)).all()

        product_map = {p.id: p for p in products}

        for item in data['items']:
            product = product_map.get(item['product_id'])
            if not product:
                return jsonify({'error': f'Product not found: {item["product_id"]}'}), 400
            item['_db_product_name'] = product.name
            item['_db_price'] = float(product.price)

        calculated_total = sum(item['_db_price'] * int(item['quantity']) for item in data['items'])
        amount_paid = float(data.get('amount_paid', calculated_total))
        if amount_paid < 0:
            return jsonify({'error': 'Amount paid cannot be negative'}), 400
        balance = round(calculated_total - amount_paid, 2)

        with _invoice_lock:
            now = datetime.now()
            year = now.year
            counter_row = InvoiceCounter.query.filter_by(year=year).first()
            if counter_row is None:
                counter_row = InvoiceCounter(year=year, counter=0)
                db.session.add(counter_row)
                db.session.flush()
            counter_row.counter += 1
            if counter_row.counter > 9999:
                return jsonify({'error': 'Invoice limit reached for this year'}), 500
            suffix = f'{counter_row.counter:04d}'
            invoice_number = f'INV-{now.strftime("%Y%m%d%H%M%S")}-{suffix}'

        new_sale = Sale(
            invoice_number=invoice_number,
            customer_name=customer_name,
            customer_mobile=customer_mobile,
            total_amount=calculated_total,
            amount_paid=amount_paid,
            balance=balance,
            payment_method=payment_method,
            sale_date=datetime.now()
        )
        db.session.add(new_sale)

        for item in data['items']:
            sale_item = SaleItem(
                sale=new_sale,
                product_id=item['product_id'],
                product_name=item['_db_product_name'],
                quantity=int(item['quantity']),
                price=item['_db_price'],
                total=item['_db_price'] * int(item['quantity'])
            )
            db.session.add(sale_item)

        db.session.commit()

        try:
            generate_invoice_pdf(new_sale)
        except Exception as pdf_err:
            logger.warning(f"PDF generation failed for {invoice_number}: {pdf_err}")

        return jsonify({'id': new_sale.id, 'invoice_number': invoice_number}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating sale: {e}")
        return jsonify({'error': 'Failed to create sale'}), 500


@app.route('/api/sales/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    sale = db.session.get(Sale, sale_id)
    if not sale:
        return jsonify({'error': 'Sale not found'}), 404
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
        'amount_paid': float(sale.amount_paid) if sale.amount_paid is not None else 0.0,
        'balance': float(sale.balance) if sale.balance is not None else 0.0,
        'payment_method': sale.payment_method or 'Cash',
        'sale_date': sale.sale_date.isoformat() if sale.sale_date else '',
        'items': items
    })


@app.route('/api/sales/<int:sale_id>', methods=['DELETE'])
def delete_sale(sale_id):
    sale = db.session.get(Sale, sale_id)
    if not sale:
        return jsonify({'error': 'Sale not found'}), 404
    try:
        pdf_path = get_cached_pdf_path(sale.invoice_number)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        db.session.delete(sale)
        db.session.commit()
        return jsonify({'message': 'Sale deleted successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting sale: {e}")
        return jsonify({'error': 'Failed to delete sale'}), 500


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
        'total_skus': total_skus
    })


def generate_invoice_pdf(sale):
    invoices_dir = os.path.join(BASE_DIR, 'invoices')
    os.makedirs(invoices_dir, exist_ok=True)
    pdf_path = os.path.join(invoices_dir, f"{sale.invoice_number}.pdf")
    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=28,
        textColor=colors.HexColor('#cc1100'),
        spaceAfter=6
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
        alignment=2,
        textColor=colors.HexColor('#333333'),
    )

    table_header_right_style = ParagraphStyle(
        'TableHeaderRight',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        alignment=2,
        textColor=colors.white,
    )
    
    footer_style = ParagraphStyle(
        'InvoiceFooter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#777777'),
        alignment=1,
        spaceBefore=20
    )
    
    story.append(Paragraph("Arun Crackers", title_style))
    story.append(Spacer(1, 10))
    
    date_str = sale.sale_date.strftime("%d-%m-%Y %I:%M %p") if sale.sale_date else datetime.now().strftime("%d-%m-%Y %I:%M %p")
    
    info_data = [
        [Paragraph("Invoice Number:", info_header_style), Paragraph(xml_escape(sale.invoice_number), info_val_style),
         Paragraph("Date & Time:", info_header_style), Paragraph(xml_escape(date_str), info_val_style)],
        [Paragraph("Customer Name:", info_header_style), Paragraph(xml_escape(sale.customer_name or "Walk-in"), info_val_style),
         Paragraph("Payment Method:", info_header_style), Paragraph(xml_escape(sale.payment_method or "Cash"), info_val_style)],
        [Paragraph("Customer Mobile:", info_header_style), Paragraph(xml_escape(sale.customer_mobile or "N/A"), info_val_style),
         Paragraph("", info_header_style), Paragraph("", info_val_style)]
    ]
    
    info_table = Table(info_data, colWidths=[110, 133.5, 110, 133.5])
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
            Paragraph(xml_escape(item.product_name), table_cell_style),
            Paragraph(f"INR {float(item.price):.2f}", table_cell_right_style),
            Paragraph(str(item.quantity), table_cell_right_style),
            Paragraph(f"INR {float(item.total):.2f}", table_cell_right_style),
        ])
        sno += 1
        
    items_table = Table(table_data, colWidths=[40, 207, 80, 70, 90])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#cc1100')),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fbfbfb')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 15))
    
    total_data = [
        [Paragraph("", info_header_style), Paragraph("Total Amount:", info_header_style), Paragraph(f"INR {float(sale.total_amount):.2f}", info_header_style)],
        [Paragraph("", info_header_style), Paragraph("Amount Paid:", info_header_style), Paragraph(f"INR {float(sale.amount_paid):.2f}", info_header_style)],
        [Paragraph("", info_header_style), Paragraph("Balance:", info_header_style), Paragraph(f"INR {float(sale.balance):.2f}", info_header_style)]
    ]
    total_table = Table(total_data, colWidths=[247, 120, 120])
    total_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    
    story.append(total_table)
    story.append(Spacer(1, 30))
    
    story.append(Paragraph("Thank you for your business! We wish you a safe and sparky celebration!", footer_style))
    story.append(Paragraph("This is a computer-generated invoice and does not require a physical signature.", footer_style))
    
    doc.build(story)
    return pdf_path


def get_cached_pdf_path(invoice_number):
    invoices_dir = os.path.join(BASE_DIR, 'invoices')
    return os.path.join(invoices_dir, f"{invoice_number}.pdf")


def _sanitize_filename(name):
    return re.sub(r'[^A-Za-z0-9_\-.]', '_', name)


@app.route('/api/sales/<int:sale_id>/pdf', methods=['GET'])
def download_sale_invoice_pdf(sale_id):
    try:
        sale = db.session.get(Sale, sale_id)
        if not sale:
            return jsonify({'error': 'Sale not found'}), 404
        pdf_path = get_cached_pdf_path(sale.invoice_number)
        if not os.path.exists(pdf_path):
            generate_invoice_pdf(sale)
        directory = os.path.dirname(pdf_path)
        filename = os.path.basename(pdf_path)
        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Error serving pdf: {e}")
        return jsonify({'error': 'Failed to download invoice'}), 500


@app.route('/api/sales/<int:sale_id>/pdf_inline', methods=['GET'])
def download_sale_invoice_pdf_inline(sale_id):
    try:
        sale = db.session.get(Sale, sale_id)
        if not sale:
            return jsonify({'error': 'Sale not found'}), 404
        pdf_path = get_cached_pdf_path(sale.invoice_number)
        if not os.path.exists(pdf_path):
            generate_invoice_pdf(sale)
        directory = os.path.dirname(pdf_path)
        filename = _sanitize_filename(os.path.basename(pdf_path))
        response = send_from_directory(directory, filename, as_attachment=False)
        response.headers['Content-Disposition'] = f'inline; filename="{filename}"'
        response.headers['Content-Type'] = 'application/pdf'
        return response
    except Exception as e:
        logger.error(f"Error serving pdf inline: {e}")
        return jsonify({'error': 'Failed to display invoice'}), 500


def init_db():
    with app.app_context():
        db.create_all()
        seed_sample_data()


def start_app():
    init_db()
    
    try:
        from waitress import serve
        logger.info("Using waitress WSGI server")
        server_thread = threading.Thread(
            target=lambda: serve(app, host='127.0.0.1', port=5000),
            daemon=True
        )
    except ImportError:
        logger.warning("waitress not installed, falling back to Flask dev server")
        server_thread = threading.Thread(
            target=lambda: app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False),
            daemon=True
        )
    server_thread.start()
    
    logger.info("=" * 60)
    logger.info(" ArunCrackers POS App is running desktop window via pywebview...")
    logger.info("=" * 60)
    
    icon_filename = "logo.ico"
    icon_path = None
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        path1 = os.path.join(exe_dir, icon_filename)
        path2 = os.path.join(sys._MEIPASS, icon_filename) if hasattr(sys, '_MEIPASS') else None
        if os.path.exists(path1):
            icon_path = path1
        elif path2 and os.path.exists(path2):
            icon_path = path2
    else:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path_in_root = os.path.join(project_root, icon_filename)
        if os.path.exists(path_in_root):
            icon_path = path_in_root
        elif os.path.exists(icon_filename):
            icon_path = os.path.abspath(icon_filename)

    window = webview.create_window(
        title="SparkBill POS",
        url="http://127.0.0.1:5000",
        width=1280,
        height=800,
        resizable=True
    )
    webview.start()



