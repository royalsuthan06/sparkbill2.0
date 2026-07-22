"""
Re-seed the database with updated inventory data.
Clears existing products and reloads from inventory_data.json.
"""
import os
import sys

# Change to backend dir so imports work
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
os.chdir(backend_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app, db
from models import Product
import json

with app.app_context():
    # Count existing
    existing_count = Product.query.count()
    print(f"Existing products in DB: {existing_count}")
    
    # Clear all products
    Product.query.delete()
    db.session.commit()
    print("Cleared all products.")
    
    # Load new data
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'inventory_data.json'))
    with open(json_path, 'r', encoding='utf-8') as f:
        items_data = json.load(f)
    
    products = [
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
    
    db.session.bulk_save_objects(products)
    db.session.commit()
    print(f"Successfully seeded {len(products)} products from inventory_data.json")
    
    # Verify
    final_count = Product.query.count()
    print(f"Final product count in DB: {final_count}")
