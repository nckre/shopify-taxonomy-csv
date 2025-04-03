import csv
import yaml
import os
from typing import Dict, List
import logging
from collections import defaultdict
import json

def load_translations(file_path: str, is_value: bool = False, is_category: bool = False) -> Dict:
    """
    Load translations from a .txt file in the format "URI : Translation"
    """
    logger = logging.getLogger(__name__)
    
    if not os.path.exists(file_path):
        logger.error(f"Translation file not found: {file_path}")
        return {}
        
    translations = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or ' : ' not in line:
                continue
                
            # Split on ' : ' to handle the format correctly
            uri, translation = line.split(' : ', 1)
            uri = uri.strip()
            translation = translation.strip()
            
            if uri and translation:
                if is_value:
                    # For values, extract just the name part before the [Attribute]
                    translation = translation.split('[')[0].strip()
                elif is_category:
                    # For categories, store both full name and name
                    translation = {
                        'full_name': translation,
                        'name': translation.split(' > ')[-1].strip()
                    }
                translations[uri] = translation
    
    return translations

def load_yaml(file_path: str) -> Dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_category_ids(version):
    category_ids = {}
    with open(f'data/output/{version}/categories.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            handle = row['shopify_uri'].split('/')[-1]
            category_ids[handle] = {
                'id': row['id'],
                'uri': row['shopify_uri']
            }
    return category_ids

def load_attribute_ids(version):
    attribute_ids = {}
    with open(f'data/output/{version}/attributes.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            attribute_ids[row['handle']] = {
                'id': row['id'],
                'uri': row['shopify_uri']
            }
    return attribute_ids

def load_value_ids(version):
    value_ids = {}
    with open(f'data/output/{version}/attribute_values.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            value_ids[row['handle']] = {
                'id': row['id'],
                'uri': row['shopify_uri']
            }
    return value_ids

def load_extended_attribute_ids(version):
    """Load extended attribute IDs from CSV"""
    extended_attribute_ids = {}
    with open(f'data/output/{version}/extended_attributes.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            extended_attribute_ids[row['handle']] = {
                'id': row['id'],
                'name': row['name']
            }
    return extended_attribute_ids

def extract_category_localizations(dist_dir: str, category_ids: Dict, lang_code: str):
    translations = load_translations(f'{dist_dir}/{lang_code}/categories.txt', is_category=True)
    localizations = []
    
    for handle, info in category_ids.items():
        if info['uri'] in translations:
            translation = translations[info['uri']]
            # Create single entry with both name and full_name
            localizations.append({
                'id': None,
                'category_id': info['id'],
                'language_code': lang_code,
                'name': translation['name'],
                'full_name': translation['full_name']
            })
    return localizations

def extract_attribute_localizations(dist_dir: str, attribute_ids: Dict, lang_code: str):
    translations = load_translations(f'{dist_dir}/{lang_code}/attributes.txt')
    localizations = []
    
    for handle, info in attribute_ids.items():
        if info['uri'] in translations:
            localizations.append({
                'id': None,
                'attribute_id': info['id'],
                'language_code': lang_code,
                'name': translations[info['uri']]
            })
    return localizations

def extract_value_localizations(dist_dir: str, value_ids: Dict, lang_code: str):
    translations = load_translations(f'{dist_dir}/{lang_code}/attribute_values.txt', is_value=True)
    localizations = []
    
    for handle, info in value_ids.items():
        if info['uri'] in translations:
            localizations.append({
                'id': None,
                'attribute_value_id': info['id'],
                'language_code': lang_code,
                'name': translations[info['uri']]
            })
    return localizations

def extract_extended_attribute_localizations(dist_dir: str, extended_attribute_ids: Dict, lang_code: str):
    """Extract extended attribute localizations from attributes.json"""
    logger = logging.getLogger(__name__)
    
    try:
        with open(f'{dist_dir}/{lang_code}/attributes.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Create a mapping of handle to translated name
        translations = {}
        for attr in data.get('attributes', []):
            for ext_attr in attr.get('extended_attributes', []):
                if 'handle' in ext_attr and 'name' in ext_attr:
                    translations[ext_attr['handle']] = ext_attr['name']
    
    except FileNotFoundError:
        logger.error(f"Attributes file not found for language {lang_code}")
        return []
    
    localizations = []
    
    for handle, info in extended_attribute_ids.items():
        if handle in translations:
            localizations.append({
                'id': None,
                'extended_attribute_id': info['id'],
                'language_code': lang_code,
                'name': translations[handle]
            })
    
    return localizations

def create_category_localizations(categories_csv: str, yaml_file: str, output_file: str):
    # Load German translations
    translations = load_yaml(yaml_file)['de']['categories']
    
    # Create mapping of shopify_uri to category id
    category_ids = {}
    with open(categories_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extract the last part of the URI as the handle
            handle = row['shopify_uri'].split('/')[-1]
            category_ids[handle] = row['id']
    
    # Create localizations CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'category_id', 'language_code', 'name'])
        
        counter = 1
        for handle, trans in translations.items():
            if handle in category_ids and 'name' in trans:
                writer.writerow([
                    counter,
                    category_ids[handle],
                    'de',
                    trans['name']
                ])
                counter += 1

def create_attribute_localizations(attributes_csv: str, yaml_file: str, output_file: str):
    # Load German translations
    translations = load_yaml(yaml_file)['de']['attributes']
    
    # Create mapping of handle to attribute id
    attribute_ids = {}
    with open(attributes_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            attribute_ids[row['handle']] = row['id']
    
    # Create localizations CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'attribute_id', 'language_code', 'name', 'description'])
        
        counter = 1
        for handle, trans in translations.items():
            if handle in attribute_ids and 'name' in trans:
                writer.writerow([
                    counter,
                    attribute_ids[handle],
                    'de',
                    trans['name'],
                    trans.get('description', '')
                ])
                counter += 1

def create_attribute_value_localizations(values_csv: str, yaml_file: str, output_file: str):
    # Load German translations
    translations = load_yaml(yaml_file)['de']['values']
    
    # Create mapping of handle to value id
    value_ids = {}
    with open(values_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            value_ids[row['handle']] = row['id']
    
    # Create localizations CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'attribute_value_id', 'language_code', 'name'])
        
        counter = 1
        for handle, trans in translations.items():
            if handle in value_ids and 'name' in trans:
                writer.writerow([
                    counter,
                    value_ids[handle],
                    'de',
                    trans['name']
                ])
                counter += 1

def validate_translations(entity_type: str, translations: List[Dict], id_mapping: Dict, language_codes: List[str]):
    """
    Validate translations and show missing entries if any
    """
    logger = logging.getLogger(__name__)
    
    total_entities = len(id_mapping)
    expected_translations = total_entities * len(language_codes)
    actual_translations = len(translations)
    
    if actual_translations < expected_translations:
        logger.warning(f"{entity_type.title()} translations: {actual_translations} found, {expected_translations} expected")
        
        # Count translations per entity to find missing ones
        translation_counts = defaultdict(int)
        for trans in translations:
            if entity_type == 'category':
                entity_id = trans['category_id']
            elif entity_type == 'attribute':
                entity_id = trans['attribute_id']
            else:  # attribute_value
                entity_id = trans['attribute_value_id']
            translation_counts[entity_id] += 1
        
        # Find entities with missing translations
        expected_count = len(language_codes)
        missing = []
        for handle, info in id_mapping.items():
            if translation_counts[info['id']] < expected_count:
                missing.append(handle)
        
        # Show first few missing entries
        if missing:
            logger.warning("First 5 entities with missing translations:")
            for handle in missing[:5]:
                count = translation_counts[id_mapping[handle]['id']]
                logger.warning(f"- {handle}: {count}/{expected_count} translations")
    
    return actual_translations < expected_translations

def extract_all_localizations(entity_type, dist_dir, id_loader, language_codes, version):
    """
    Extract localizations for all configured languages for a given entity type
    """
    all_localizations = []
    entity_ids = id_loader(version)
    counter = 1
    
    for lang in language_codes:
        if entity_type == 'category':
            localizations = extract_category_localizations(dist_dir, entity_ids, lang)
        elif entity_type == 'attribute':
            localizations = extract_attribute_localizations(dist_dir, entity_ids, lang)
        else:  # attribute_value
            localizations = extract_value_localizations(dist_dir, entity_ids, lang)
        
        # Update IDs to continue from last counter
        for loc in localizations:
            loc['id'] = counter
            counter += 1
        
        all_localizations.extend(localizations)
    
    # Validate translations
    validate_translations(entity_type, all_localizations, entity_ids, language_codes)
    
    return all_localizations

def extract_vertical_localizations(dist_dir: str, verticals: Dict, lang_code: str):
    """
    Extract vertical localizations from taxonomy.json
    """
    logger = logging.getLogger(__name__)
    
    try:
        with open(f'{dist_dir}/{lang_code}/taxonomy.json', 'r', encoding='utf-8') as f:
            taxonomy_data = json.load(f)
            translations = {v['prefix']: v['name'] for v in taxonomy_data.get('verticals', [])}
    except FileNotFoundError:
        logger.error(f"Taxonomy file not found for language {lang_code}")
        return []
    
    localizations = []
    
    for vertical_id, info in verticals.items():
        if info['prefix'] in translations:
            localizations.append({
                'id': None,
                'vertical_id': vertical_id,
                'language_code': lang_code,
                'name': translations[info['prefix']]
            })
    
    return localizations

def load_vertical_ids(version):
    vertical_ids = {}
    with open(f'data/output/{version}/verticals.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            vertical_ids[row['id']] = {
                'prefix': row['prefix'],
                'name': row['name']
            }
    return vertical_ids

def extract_all_vertical_localizations(dist_dir: str, language_codes: List[str], version: str):
    """
    Extract vertical localizations for all configured languages
    """
    all_localizations = []
    vertical_ids = load_vertical_ids(version)
    counter = 1
    
    for lang in language_codes:
        localizations = extract_vertical_localizations(dist_dir, vertical_ids, lang)
        
        # Update IDs to continue from last counter
        for loc in localizations:
            loc['id'] = counter
            counter += 1
        
        all_localizations.extend(localizations)
    
    # Validate translations
    validate_translations('vertical', all_localizations, 
                        {k: {'id': k} for k in vertical_ids.keys()}, 
                        language_codes)
    
    return all_localizations

def extract_all_extended_attribute_localizations(dist_dir: str, language_codes: List[str], version: str):
    """Extract extended attribute localizations for all configured languages"""
    all_localizations = []
    extended_attribute_ids = load_extended_attribute_ids(version)
    counter = 1
    
    for lang in language_codes:
        localizations = extract_extended_attribute_localizations(dist_dir, extended_attribute_ids, lang)
        
        # Update IDs to continue from last counter
        for loc in localizations:
            loc['id'] = counter
            counter += 1
        
        all_localizations.extend(localizations)
    
    # Validate translations
    validate_translations('extended_attribute', all_localizations, 
                        {k: {'id': k} for k in extended_attribute_ids.keys()}, 
                        language_codes)
    
    return all_localizations

def main():
    # Define input/output paths
    input_dir = 'data/output/2025-01-unstable'
    yaml_dir = 'data/input/2025-01-unstable/localizations'
    output_dir = 'data/output/2025-01-unstable/localizations'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process categories
    create_category_localizations(
        f'{input_dir}/categories.csv',
        f'{yaml_dir}/categories/de.yml',
        f'{output_dir}/localizations_category.csv'
    )
    
    # Process attributes
    create_attribute_localizations(
        f'{input_dir}/attributes.csv',
        f'{yaml_dir}/attributes/de.yml',
        f'{output_dir}/localizations_attribute.csv'
    )
    
    # Process attribute values
    create_attribute_value_localizations(
        f'{input_dir}/attribute_values.csv',
        f'{yaml_dir}/values/de.yml',
        f'{output_dir}/localizations_attribute_value.csv'
    )

if __name__ == "__main__":
    main()
