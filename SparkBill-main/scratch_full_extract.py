"""
Full PDF extraction script - scans every page and every table
to ensure we capture ALL items from the price list.
"""
import pdfplumber
import json
import re

pdf_path = r"Arun_crackers_print_pricelist_finalout_2025_removed.pdf"

all_rows = []
page_stats = []

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    for page_num, page in enumerate(pdf.pages, 1):
        tables = page.extract_tables()
        print(f"\n=== Page {page_num}: {len(tables)} table(s) ===")
        
        for t_idx, table in enumerate(tables):
            print(f"  Table {t_idx}: {len(table)} rows")
            for r_idx, row in enumerate(table):
                # Clean each cell
                cleaned = []
                for cell in row:
                    if cell is None:
                        cleaned.append('')
                    else:
                        # Clean non-ASCII artifacts
                        c = cell.encode('ascii', 'ignore').decode('ascii').strip()
                        cleaned.append(c)
                
                # Print first few rows for inspection
                if r_idx < 5:
                    print(f"    Row {r_idx}: {cleaned}")
                
                all_rows.append({
                    'page': page_num,
                    'table': t_idx,
                    'row_idx': r_idx,
                    'cells': cleaned,
                    'raw_cells': [c if c else '' for c in row]
                })

print(f"\n\nTotal raw rows across all pages/tables: {len(all_rows)}")

# Now try to identify product rows
# A product row typically has: S.No (numeric), Content (description), Actual Rate, Our Rate
# Let's look at column patterns

print("\n\n=== Analyzing column patterns ===")
# Group by (page, table) to find header rows
from collections import defaultdict
groups = defaultdict(list)
for r in all_rows:
    groups[(r['page'], r['table'])].append(r)

products = []
current_category = ""

for key in sorted(groups.keys()):
    rows = groups[key]
    print(f"\n--- Page {key[0]}, Table {key[1]} ({len(rows)} rows) ---")
    
    for row_data in rows:
        cells = row_data['cells']
        raw_cells = row_data['raw_cells']
        
        # Skip empty rows
        if all(c == '' for c in cells):
            continue
        
        # Try to detect category header rows - they usually span multiple columns
        # and don't have a numeric S.No
        non_empty = [c for c in cells if c.strip()]
        
        # Check if first cell looks like a serial number
        first_cell = cells[0].strip() if cells else ''
        
        # Is this a numeric S.No?
        is_serial = bool(re.match(r'^\d{1,3}$', first_cell))
        
        if not is_serial:
            # Could be a category header or other non-product row
            # Category headers tend to be single text spanning the row
            combined = ' '.join(c for c in cells if c.strip())
            if combined and not any(kw in combined.upper() for kw in ['S.NO', 'ACTUAL', 'RATE', 'CONTENT', 'QTY', 'OUR OFFER']):
                # Could be a category
                if len(non_empty) <= 3 and len(combined) > 3:
                    # Check if it looks like a category name (not just numbers)
                    if not re.match(r'^[\d\s.,]+$', combined):
                        potential_cat = combined.strip()
                        if potential_cat:
                            current_category = potential_cat
                            print(f"  [CATEGORY]: {current_category}")
            continue
        
        # This is a product row with serial number
        # Try to extract: S.No, Content, Qty/Pack, Actual Rate, Our Rate
        # The column structure varies, let's be flexible
        
        sno = first_cell
        
        # Find the content/name - usually the second column
        name = ''
        actual_rate = 0
        our_rate = 0
        
        # Look through remaining cells for name and prices
        numeric_cells = []
        text_cells = []
        
        for i, c in enumerate(cells[1:], 1):
            c = c.strip()
            if not c:
                continue
            # Try to parse as number
            try:
                val = float(c.replace(',', ''))
                numeric_cells.append((i, val))
            except (ValueError, AttributeError):
                text_cells.append((i, c))
        
        # Name is usually the first text cell
        if text_cells:
            name = text_cells[0][1]
        
        # Last two numeric values are typically Actual Rate and Our Rate
        if len(numeric_cells) >= 2:
            actual_rate = numeric_cells[-2][1]
            our_rate = numeric_cells[-1][1]
        elif len(numeric_cells) == 1:
            actual_rate = numeric_cells[0][1]
            our_rate = numeric_cells[0][1]
        
        if name and our_rate > 0:
            products.append({
                'sno': sno,
                'name': name,
                'category': current_category,
                'mrp': actual_rate,
                'price': our_rate,
                'page': key[0],
                'raw': [c for c in cells if c.strip()]
            })
            if len(products) % 20 == 0:
                print(f"  ... {len(products)} products so far ...")

print(f"\n\n=== RESULTS ===")
print(f"Total products extracted: {len(products)}")
print(f"\nCategories found:")
cats = defaultdict(int)
for p in products:
    cats[p['category']] += 1
for cat, count in sorted(cats.items()):
    print(f"  {cat}: {count}")

# Show all products
print(f"\n\n=== ALL PRODUCTS ===")
for i, p in enumerate(products):
    print(f"  {p['sno']:>3}. {p['name'][:50]:<50} MRP={p['mrp']:>8.1f}  Price={p['price']:>8.1f}  [{p['category']}]")

# Save to temp file for analysis
with open('scratch_full_extract_results.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=2, ensure_ascii=False)
print(f"\nSaved to scratch_full_extract_results.json")
