import os
import sys
import json
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app, db
from models import Product, Sale, SaleItem


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

    import sqlalchemy as sa
    with app.app_context():
        engines = db._app_engines.setdefault(app, {})
        for e in engines.values():
            e.dispose()
        engines.clear()
        engines[None] = sa.create_engine(f'sqlite:///{db_path}')

        db.create_all()
        p1 = Product(sku='T01', name='Test Sparkler', price=50.0, category='Sparklers')
        p2 = Product(sku='T02', name='Test Rocket', price=120.0, category='Rockets')
        db.session.add_all([p1, p2])
        db.session.commit()

    with app.test_client() as client:
        yield client

    with app.app_context():
        db.drop_all()
        engines = db._app_engines.get(app, {})
        for e in engines.values():
            e.dispose()
        engines.clear()
    os.close(db_fd)
    os.unlink(db_path)


# --- Product Routes ---

def test_get_products(client):
    res = client.get('/api/products')
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 2
    assert data[0]['sku'] == 'T01'


def test_get_products_empty(client):
    with app.app_context():
        db.session.query(Product).delete()
        db.session.commit()
    res = client.get('/api/products')
    assert res.status_code == 200
    assert res.get_json() == []


def test_lookup_product(client):
    res = client.get('/api/products/lookup/T01')
    assert res.status_code == 200
    assert res.get_json()['name'] == 'Test Sparkler'


def test_lookup_product_not_found(client):
    res = client.get('/api/products/lookup/NONEXISTENT')
    assert res.status_code == 404


def test_add_product(client):
    res = client.post('/api/products', json={
        'sku': 'T03', 'name': 'Test Bomb', 'price': 99.0, 'category': 'Sound'
    })
    assert res.status_code == 201
    assert 'id' in res.get_json()

    res2 = client.get('/api/products/lookup/T03')
    assert res2.status_code == 200
    assert res2.get_json()['name'] == 'Test Bomb'


def test_add_product_duplicate_sku(client):
    res = client.post('/api/products', json={
        'sku': 'T01', 'name': 'Dup', 'price': 10.0
    })
    assert res.status_code == 400


def test_add_product_missing_fields(client):
    res = client.post('/api/products', json={'name': 'No SKU'})
    assert res.status_code == 400


def test_add_product_negative_price(client):
    res = client.post('/api/products', json={
        'sku': 'TNEG', 'name': 'Neg', 'price': -5.0
    })
    assert res.status_code == 400


def test_update_product(client):
    with app.app_context():
        p = Product.query.filter_by(sku='T01').first()
        pid = p.id
    res = client.put(f'/api/products/{pid}', json={
        'sku': 'T01', 'name': 'Updated Sparkler', 'price': 75.0, 'category': 'Sparklers'
    })
    assert res.status_code == 200

    res2 = client.get('/api/products/lookup/T01')
    assert res2.get_json()['name'] == 'Updated Sparkler'
    assert res2.get_json()['price'] == 75.0


def test_update_product_not_found(client):
    res = client.put('/api/products/9999', json={'name': 'X', 'price': 1.0, 'sku': 'X'})
    assert res.status_code == 404


def test_delete_product(client):
    with app.app_context():
        p = Product.query.filter_by(sku='T02').first()
        pid = p.id
    res = client.delete(f'/api/products/{pid}')
    assert res.status_code == 200

    res2 = client.get('/api/products/lookup/T02')
    assert res2.status_code == 404


# --- Sale Routes ---

def _create_sale_payload(client):
    with app.app_context():
        p = Product.query.filter_by(sku='T01').first()
        pid = p.id
        pname = p.name
        price = float(p.price)
    return {
        'customer_name': 'Test Customer',
        'customer_mobile': '9999999999',
        'total_amount': price * 3,
        'amount_paid': price * 3,
        'balance': 0,
        'payment_method': 'Cash',
        'items': [{
            'product_id': pid,
            'product_name': pname,
            'quantity': 3,
            'price': price,
        }]
    }


def test_create_sale(client):
    res = client.post('/api/sales', json=_create_sale_payload(client))
    assert res.status_code == 201
    data = res.get_json()
    assert 'id' in data
    assert data['invoice_number'].startswith('INV-')


def test_create_sale_empty_items(client):
    res = client.post('/api/sales', json={'items': [], 'total_amount': 0, 'amount_paid': 0})
    assert res.status_code == 400


def test_create_sale_total_mismatch(client):
    payload = _create_sale_payload(client)
    payload['total_amount'] = 99999
    res = client.post('/api/sales', json=payload)
    assert res.status_code == 201


def test_create_sale_negative_quantity(client):
    payload = _create_sale_payload(client)
    payload['items'][0]['quantity'] = -1
    res = client.post('/api/sales', json=payload)
    assert res.status_code == 400


def test_get_sales(client):
    client.post('/api/sales', json=_create_sale_payload(client))
    client.post('/api/sales', json=_create_sale_payload(client))
    res = client.get('/api/sales')
    assert res.status_code == 200
    data = res.get_json()
    assert 'sales' in data
    assert len(data['sales']) == 2
    assert data['total'] == 2


def test_get_sale_detail(client):
    res = client.post('/api/sales', json=_create_sale_payload(client))
    sale_id = res.get_json()['id']
    res2 = client.get(f'/api/sales/{sale_id}')
    assert res2.status_code == 200
    data = res2.get_json()
    assert data['customer_name'] == 'Test Customer'
    assert len(data['items']) == 1


def test_get_sale_not_found(client):
    res = client.get('/api/sales/9999')
    assert res.status_code == 404


def test_invoice_number_unique(client):
    r1 = client.post('/api/sales', json=_create_sale_payload(client))
    r2 = client.post('/api/sales', json=_create_sale_payload(client))
    inv1 = r1.get_json()['invoice_number']
    inv2 = r2.get_json()['invoice_number']
    assert inv1 != inv2
    suffix1 = int(inv1.rsplit('-', 1)[1])
    suffix2 = int(inv2.rsplit('-', 1)[1])
    assert suffix2 == suffix1 + 1


def test_delete_sale(client):
    res = client.post('/api/sales', json=_create_sale_payload(client))
    sale_id = res.get_json()['id']
    res2 = client.delete(f'/api/sales/{sale_id}')
    assert res2.status_code == 200
    res3 = client.get(f'/api/sales/{sale_id}')
    assert res3.status_code == 404


def test_delete_sale_not_found(client):
    res = client.delete('/api/sales/9999')
    assert res.status_code == 404


# --- Stats Route ---

def test_stats(client):
    res = client.get('/api/stats')
    assert res.status_code == 200
    data = res.get_json()
    assert data['total_skus'] == 2
    assert 'today_sales' in data
    assert 'today_count' in data
