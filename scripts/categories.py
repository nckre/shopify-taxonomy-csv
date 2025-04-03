import json
import csv

def load_vertical_ids(version):
    vertical_ids = {}
    with open(f'data/output/{version}/verticals.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            vertical_ids[row['prefix']] = row['id']
    return vertical_ids

def extract_categories(json_file_path, vertical_ids):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    categories = []
    shopify_to_serial_id = {}
    serial_id = 1

    # First pass: Create categories with serial IDs and build mapping
    for vertical in data.get('verticals', []):
        vertical_prefix = vertical.get('prefix')
        vertical_id = vertical_ids.get(vertical_prefix)
        
        for category in vertical.get('categories', []):
            shopify_uri = category.get('id')
            shopify_id = shopify_uri.split('/')[-1] if shopify_uri else None
            
            # Store mapping of shopify_id to serial_id
            shopify_to_serial_id[shopify_id] = serial_id
            
            categories.append({
                'id': serial_id,
                'shopify_id': shopify_id,
                'shopify_uri': shopify_uri,
                'level': category.get('level'),
                'name': category.get('name'),
                'full_name': category.get('full_name'),
                'parent_shopify_id': category.get('parent_id', '').split('/')[-1] if category.get('parent_id') else None,
                'vertical_id': vertical_id
            })
            serial_id += 1

    # Second pass: Update parent_id references
    for category in categories:
        parent_shopify_id = category.pop('parent_shopify_id')  # Remove the temporary field
        category['parent_id'] = shopify_to_serial_id.get(parent_shopify_id) if parent_shopify_id else None

    return categories