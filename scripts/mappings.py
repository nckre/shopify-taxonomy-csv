import json
import csv

def load_attribute_ids(version):
    attribute_ids = {}
    with open(f'data/output/{version}/attributes.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            attribute_ids[row['shopify_id']] = row['id']
    return attribute_ids

def load_attribute_value_ids(version):
    value_ids = {}
    with open(f'data/output/{version}/attribute_values.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            value_ids[row['shopify_id']] = row['id']
    return value_ids

def create_attribute_value_mappings(json_file_path, attribute_ids, value_ids):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    mappings = []
    for attribute in data.get('attributes', []):
        attribute_id = attribute.get('id').split('/')[-1]  # Extract the ID from the URI
        if not attribute_id or attribute_id not in attribute_ids:
            continue

        attribute_serial_id = attribute_ids[attribute_id]
        
        # Process value mappings
        for value in attribute.get('values', []):
            value_id = value.get('id').split('/')[-1]  # Extract the ID from the URI
            if value_id and value_id in value_ids:
                mappings.append({
                    'attribute_id': attribute_serial_id,
                    'value_id': value_ids[value_id]
                })
    
    return mappings

def load_category_ids(version):
    category_ids = {}
    with open(f'data/output/{version}/categories.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            category_ids[row['shopify_id']] = row['id']
    return category_ids

def create_category_attribute_mappings(json_file_path, category_ids, attribute_ids, extended_attribute_ids):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    mappings = []
    # Iterate through verticals and their nested categories
    for vertical in data.get('verticals', []):
        for category in vertical.get('categories', []):
            category_id = category.get('id').split('/')[-1]  # Extract the ID from the URI
            if not category_id or category_id not in category_ids:
                continue

            category_serial_id = category_ids[category_id]
            
            # Process attributes
            for attribute in category.get('attributes', []):
                attribute_id = attribute.get('id').split('/')[-1]  # Extract the ID from the URI
                if attribute_id and attribute_id in attribute_ids:
                    mapping = {
                        'category_id': category_serial_id,
                        'attribute_id': attribute_ids[attribute_id]
                    }
                    
                    # If this is an extended attribute, add the extended_attribute_id
                    if attribute.get('extended') and attribute.get('handle') in extended_attribute_ids:
                        mapping['extended_attribute_id'] = extended_attribute_ids[attribute['handle']]
                    else:
                        mapping['extended_attribute_id'] = 'NULL'
                    
                    mappings.append(mapping)

            # Process nested children categories recursively
            def process_children(children):
                for child in children:
                    child_id = child.get('id').split('/')[-1]  # Extract the ID from the URI
                    if child_id and child_id in category_ids:
                        child_serial_id = category_ids[child_id]
                        
                        for attribute in child.get('attributes', []):
                            attribute_id = attribute.get('id').split('/')[-1]  # Extract the ID from the URI
                            if attribute_id and attribute_id in attribute_ids:
                                mapping = {
                                    'category_id': child_serial_id,
                                    'attribute_id': attribute_ids[attribute_id]
                                }
                                
                                # If this is an extended attribute, add the extended_attribute_id
                                if attribute.get('extended') and attribute.get('handle') in extended_attribute_ids:
                                    mapping['extended_attribute_id'] = extended_attribute_ids[attribute['handle']]
                                else:
                                    mapping['extended_attribute_id'] = 'NULL'
                                
                                mappings.append(mapping)
                        
                        # Recursively process this child's children
                        if child.get('children'):
                            process_children(child['children'])

            # Start processing children if they exist
            if category.get('children'):
                process_children(category['children'])
    
    return mappings

def create_attribute_extended_mappings(json_file_path, attribute_ids, extended_attribute_ids):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    mappings = []
    for attribute in data.get('attributes', []):
        attribute_id = attribute.get('id').split('/')[-1]  # Extract the ID from the URI
        if not attribute_id or attribute_id not in attribute_ids:
            continue

        attribute_serial_id = attribute_ids[attribute_id]
        
        # Process extended attributes
        for ext_attr in attribute.get('extended_attributes', []):
            ext_handle = ext_attr.get('handle')
            if ext_handle and ext_handle in extended_attribute_ids:
                mappings.append({
                    'attribute_id': attribute_serial_id,
                    'extended_attribute_id': extended_attribute_ids[ext_handle]
                })
    
    return mappings

def load_extended_attribute_ids(version):
    extended_attribute_ids = {}
    with open(f'data/output/{version}/extended_attributes.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            extended_attribute_ids[row['handle']] = row['id']
    return extended_attribute_ids