"""
Build the final clean inventory JSON from the full extraction results.
Handles:
  - Duplicate serial numbers by generating unique SKUs
  - Cleans product names (removes trailing redundant numbers/text)
  - Adds the newly discovered Gift Box category
"""
import json
import re

with open('scratch_full_extract_results.json', 'r', encoding='utf-8') as f:
    raw_products = json.load(f)

print(f"Raw products from extraction: {len(raw_products)}")

# Load existing inventory to preserve any manual fixes
with open('database/inventory_data.json', 'r', encoding='utf-8') as f:
    existing = json.load(f)
print(f"Existing inventory items: {len(existing)}")
existing_names = {item['name'] for item in existing}

def clean_name(name, sno):
    """Clean up product name - remove trailing duplicate numbers and artifacts."""
    # Remove newlines
    name = name.replace('\n', ' ').replace('\r', ' ')
    # Collapse multiple spaces
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Remove trailing serial number duplicates like "2 3/4" at end if it matches beginning
    # Remove trailing number that matches serial number
    # e.g. "FANCY 2" -> "FANCY" when sno is 2
    # But be careful not to remove meaningful numbers
    
    # Remove trailing repetition of size/number patterns that duplicate the prefix
    # e.g. "7 CM AMBER ELECTRIC 7 CM" -> "7 CM AMBER ELECTRIC"  
    # e.g. "1000 WALA 1000" -> "1000 WALA"
    parts = name.split()
    if len(parts) > 2:
        # Check if the last N tokens match the first N tokens
        for n in range(1, min(4, len(parts)//2 + 1)):
            if parts[-n:] == parts[:n]:
                name = ' '.join(parts[:-n])
                break
    
    # Remove trailing "50/50" style duplicates
    name = re.sub(r'\s+50/50$', '', name)
    # Remove trailing "(4IN1)" style duplicates  
    name = re.sub(r'\s+\(4\s*IN\s*1\)$', '', name)
    # Remove trailing content in parens that duplicates earlier content
    # e.g. "(16 ITEM BOX) (16 ITEM BOX)" -> "(16 ITEM BOX)"
    match = re.search(r'(\([^)]+\))\s+\1$', name)
    if match:
        name = name[:match.start()] + match.group(1)
    
    return name.strip()

# Build the complete list
final_products = []
used_skus = set()

def get_unique_sku(base_sku):
    """Generate a unique SKU, adding suffix if needed."""
    sku = base_sku
    if sku not in used_skus:
        used_skus.add(sku)
        return sku
    suffix = ord('a')
    while f"{sku}{chr(suffix)}" in used_skus:
        suffix += 1
    unique = f"{sku}{chr(suffix)}"
    used_skus.add(unique)
    return unique

for p in raw_products:
    sno = p['sno']
    base_sku = sno.zfill(3) if len(sno) < 3 else sno
    sku = get_unique_sku(base_sku)
    
    name = clean_name(p['name'], sno)
    category = p['category'].strip()
    
    # Clean category: title case and remove redundant suffixes
    # e.g. "7 CM SPARKLERS 7 CM" -> "7 Cm Sparklers"
    cat_parts = category.split()
    if len(cat_parts) > 2:
        for n in range(1, min(4, len(cat_parts)//2 + 1)):
            if cat_parts[-n:] == cat_parts[:n]:
                category = ' '.join(cat_parts[:-n])
                break
    
    # Title case the category
    category = category.title()
    # Fix common title case issues
    category = category.replace(' Of ', ' of ')
    category = category.replace('Cm', 'CM')
    category = category.replace(' In ', ' in ')
    
    mrp = p['mrp']
    price = p['price']
    cost_price = round(price * 0.65, 2)  # Estimated cost at 65% of our price
    
    # Build description
    desc = f"1 PKT - {name}"
    
    final_products.append({
        "sku": sku,
        "name": name,
        "description": desc,
        "price": price,
        "cost_price": cost_price,
        "mrp": mrp,
        "stock_quantity": 100,
        "category": category
    })

print(f"\nFinal product count: {len(final_products)}")

# Show categories
from collections import Counter
cats = Counter(p['category'] for p in final_products)
print("\nCategories:")
for cat, count in sorted(cats.items()):
    print(f"  {cat}: {count}")

# Show new items not in existing
new_items = [p for p in final_products if p['name'] not in existing_names]
print(f"\nNew items not in previous inventory: {len(new_items)}")
for p in new_items:
    print(f"  [{p['sku']}] {p['name']} - Rs.{p['price']} (MRP: Rs.{p['mrp']}) [{p['category']}]")

# Write the final inventory
with open('database/inventory_data.json', 'w', encoding='utf-8') as f:
    json.dump(final_products, f, indent=2, ensure_ascii=False)
print(f"\nSaved {len(final_products)} products to database/inventory_data.json")
