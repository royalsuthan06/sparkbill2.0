import os
import sys
import json

# Setup paths to import from backend
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'backend')

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from backend.app import app, db
from backend.models import Product

def sync_inventory():
    """Reads inventory_data.json and adds missing items to the database."""
    with app.app_context():
        json_path = os.path.abspath(os.path.join(current_dir, 'database', 'inventory_data.json'))
        if not os.path.exists(json_path):
            print(f"Inventory file not found: {json_path}")
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            items_data = json.load(f)

        added_count = 0
        updated_count = 0

        for item in items_data:
            sku = str(item['sku'])
            existing_product = Product.query.filter_by(sku=sku).first()
            
            if not existing_product:
                # Add new product
                new_product = Product(
                    sku=sku,
                    name=str(item['name']),
                    description=str(item.get('description', '')),
                    price=float(item['price']),
                    cost_price=float(item.get('cost_price', 0)),
                    mrp=float(item['mrp']),
                    stock_quantity=int(item.get('stock_quantity', 100)),
                    category=str(item.get('category', 'General'))
                )
                db.session.add(new_product)
                added_count += 1
            else:
                # Update existing product (optional based on your needs)
                existing_product.name = str(item['name'])
                existing_product.price = float(item['price'])
                existing_product.mrp = float(item['mrp'])
                updated_count += 1
                
        db.session.commit()
        print(f"Sync complete. Added {added_count} new items. Updated {updated_count} existing items.")
        print(f"Total products in database: {Product.query.count()}")

if __name__ == '__main__':
    sync_inventory()
