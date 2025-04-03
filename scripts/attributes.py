import json

def extract_attributes_and_extended(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    attributes = []
    # Use a dictionary to store unique extended attributes (handle as key to ensure uniqueness)
    extended_attrs_dict = {}
    
    for i, attribute in enumerate(data.get('attributes', []), 1):
        # Process main attributes
        attributes.append({
            'id': i,
            'name': attribute.get('name'),
            'handle': attribute.get('handle'),
            'description': attribute.get('description'),
            'shopify_id': attribute.get('id').split('/')[-1],  # Extract the ID from the URI
            'shopify_uri': attribute.get('id')  # Store the full URI
        })
        
        # Collect extended attributes
        for ext_attr in attribute.get('extended_attributes', []):
            handle = ext_attr.get('handle')
            if handle and handle not in extended_attrs_dict:
                extended_attrs_dict[handle] = {
                    'name': ext_attr.get('name'),
                    'handle': handle
                }
    
    # Convert extended attributes dictionary to list with serial IDs
    extended_attributes = [
        {'id': i, **attr_data}
        for i, attr_data in enumerate(extended_attrs_dict.values(), 1)
    ]
    
    return attributes, extended_attributes