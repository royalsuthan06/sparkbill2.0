"""
Final clean pass on inventory_data.json:
- Remove trailing size duplicates from names (e.g. "KURUVI CRACKERS 2 3/4" -> "KURUVI CRACKERS")
- Remove trailing numbers that match the serial no from content column noise
- Clean up multiline name artifacts
"""
import json
import re

with open('database/inventory_data.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"Products to clean: {len(products)}")

def deep_clean_name(name):
    """More aggressive name cleaning."""
    # Remove newlines
    name = name.replace('\n', ' ').replace('\r', ' ')
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Remove trailing standalone numbers like "2 3/4", "3.5", "4", "10.5", etc.
    # that are size artifacts from the PDF table
    # Pattern: trailing number (possibly with fractions or decimals) at end
    name = re.sub(r'\s+\d+\s*\d*/?\d*\s*$', '', name)
    # Also handle "2 1/2" at end
    name = re.sub(r'\s+\d+\s+\d+/\d+\s*$', '', name)
    
    # Remove trailing "10 CM", "7 CM", "30 CM" etc (size echoes from sparkler categories)
    name = re.sub(r'\s+\d+\s*CM\s*$', '', name, flags=re.IGNORECASE)
    
    # Remove trailing "50/50" 
    name = re.sub(r'\s+50/50\s*$', '', name)
    
    # Remove trailing "(4IN1)" or "(4 IN 1)"
    name = re.sub(r'\s+\(4\s*IN\s*1\)\s*$', '', name, flags=re.IGNORECASE)
    
    # Remove duplicate trailing parenthetical 
    # e.g. "(16 ITEM BOX) (16 ITEM BOX)" -> "(16 ITEM BOX)"
    match = re.search(r'(\([^)]+\))\s+\1\s*$', name)
    if match:
        name = name[:match.start()] + ' ' + match.group(1)
    
    # Remove trailing "240" type numbers that are shot counts echoed
    # Only if it's a standalone number at end and name is long enough
    if len(name.split()) > 3:
        name = re.sub(r'\s+\d{2,}$', '', name)
    
    return name.strip()

changed = 0
for p in products:
    old_name = p['name']
    new_name = deep_clean_name(old_name)
    if new_name != old_name:
        print(f"  '{old_name}' -> '{new_name}'")
        p['name'] = new_name
        p['description'] = f"1 PKT - {new_name}"
        changed += 1

print(f"\nCleaned {changed} product names")

# Verify no empty names
empty = [p for p in products if not p['name'].strip()]
if empty:
    print(f"WARNING: {len(empty)} products with empty names!")
    for p in empty:
        print(f"  SKU {p['sku']}: raw='{p['name']}'")

# Write back
with open('database/inventory_data.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=2, ensure_ascii=False)

# Print final list
print(f"\n=== FINAL INVENTORY ({len(products)} items) ===")
for p in products:
    print(f"  [{p['sku']:>4}] {p['name'][:55]:<55} Price={p['price']:>8.1f}  MRP={p['mrp']:>8.1f}  [{p['category']}]")
