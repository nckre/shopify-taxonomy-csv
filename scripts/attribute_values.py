import json

def extract_attribute_values(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    values = []
    for i, value in enumerate(data.get('values', []), 1):
        shopify_uri = value.get('id')
        shopify_id = shopify_uri.split('/')[-1] if shopify_uri else None
        
        values.append({
            'id': i,
            'shopify_id': shopify_id,
            'shopify_uri': shopify_uri,
            'name': value.get('name'),
            'handle': value.get('handle')
        })

    return values