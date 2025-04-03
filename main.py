import scripts.verticals
import scripts.categories
import scripts.attributes
import scripts.attribute_values
import scripts.mappings
import scripts.utils
import scripts.localizations
import logging
import os
import csv
import json

# Configuration
version = '2025-06-unstable'
source_language_code = 'en'  # Default source language
language_codes = ['fi', 'sv']

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def ensure_output_directories():
    output_dir = f'data/output/{version}'
    os.makedirs(output_dir, exist_ok=True)

def write_verticals(data):
    scripts.utils.write_csv(
        data,
        ['id', 'name', 'prefix'],
        f'data/output/{version}/verticals.csv'
    )

def write_categories(data):
    scripts.utils.write_csv(
        data,
        ['id', 'shopify_id', 'shopify_uri', 'level', 'name', 'full_name', 'parent_id', 'vertical_id'],
        f'data/output/{version}/categories.csv'
    )

def write_attributes(data):
    attributes_info, extended_attributes_info = data
    scripts.utils.write_csv(
        attributes_info,
        ['id', 'name', 'handle', 'description', 'shopify_id', 'shopify_uri'],
        f'data/output/{version}/attributes.csv'
    )
    scripts.utils.write_csv(
        extended_attributes_info,
        ['id', 'name', 'handle'],
        f'data/output/{version}/extended_attributes.csv'
    )

def write_attribute_values(data):
    scripts.utils.write_csv(
        data,
        ['id', 'shopify_id', 'shopify_uri', 'name', 'handle'],
        f'data/output/{version}/attribute_values.csv'
    )

def write_mappings(data):
    scripts.utils.write_csv(
        data,
        ['attribute_id', 'value_id'],
        f'data/output/{version}/attribute_value_mappings.csv'
    )

def write_category_attribute_mappings(data):
    scripts.utils.write_csv(
        data,
        ['category_id', 'extended_attribute_id', 'attribute_id'],
        f'data/output/{version}/category_attribute_mappings.csv'
    )

def write_attribute_extended_mappings(data):
    scripts.utils.write_csv(
        data,
        ['attribute_id', 'extended_attribute_id'],
        f'data/output/{version}/attribute_extended_mappings.csv'
    )

def write_localizations(data, entity_type):
    # Define headers based on entity type
    if entity_type == 'category':
        headers = ['id', 'category_id', 'language_code', 'name', 'full_name']
    elif entity_type == 'attribute':
        headers = ['id', 'attribute_id', 'language_code', 'name']
    elif entity_type == 'vertical':
        headers = ['id', 'vertical_id', 'language_code', 'name']
    elif entity_type == 'extended_attribute':
        headers = ['id', 'extended_attribute_id', 'language_code', 'name']
    else:  # attribute_value
        headers = ['id', 'attribute_value_id', 'language_code', 'name']
    
    scripts.utils.write_csv(
        data,
        headers,
        f'data/output/{version}/localizations/localizations_{entity_type}.csv'
    )

def check_and_remove_duplicates(file_path):
    logger = logging.getLogger(__name__)
    
    # Read the CSV file
    rows = []
    duplicates = []
    seen = set()
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        
        for row in reader:
            # Create a tuple of the non-empty values to use as a hash key
            # Handle different file types appropriately
            if 'category_id' in headers and 'extended_attribute_id' in headers:
                # For category_attribute_mappings.csv, compare all three fields
                row_tuple = (
                    row['category_id'],
                    row['attribute_id'],
                    row.get('extended_attribute_id', '')  # Use empty string if not present
                )
            elif 'extended_attribute_id' in headers:
                # For attribute_extended_mappings.csv, compare both fields
                row_tuple = (
                    row['attribute_id'],
                    row['extended_attribute_id']
                )
            else:
                # For other files, compare all fields
                row_tuple = tuple(row.values())
            
            if row_tuple in seen:
                duplicates.append(row)
            else:
                seen.add(row_tuple)
                rows.append(row)
    
    # Only log if duplicates are found
    if duplicates:
        logger.warning(f"Found {len(duplicates)} duplicate entries")
        
        # Write back the deduplicated data
        with open(file_path, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

def extract_all_localizations(entity_type, yaml_dir, id_loader):
    """
    Wrapper function to pass language_codes and version to the actual implementation
    """
    return scripts.localizations.extract_all_localizations(
        entity_type, 
        yaml_dir, 
        id_loader, 
        language_codes,
        version  # Pass the version from main.py
    )

def check_version_consistency(version, source_language_code):
    logger = logging.getLogger(__name__)
    taxonomy_path = f'data/input/{version}/dist/{source_language_code}/taxonomy.json'
    
    try:
        with open(taxonomy_path, 'r', encoding='utf-8') as f:
            taxonomy_data = json.load(f)
            
        taxonomy_version = taxonomy_data.get('version')
        if taxonomy_version != version:
            raise ValueError(
                f"Version mismatch: Script version '{version}' does not match "
                f"taxonomy.json version '{taxonomy_version}'"
            )
        logger.info(f"Version check passed: {version}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Taxonomy file not found: {taxonomy_path}")

def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Add version check
        logger.info("Step 1: Version check")
        check_version_consistency(version, source_language_code)
        logger.info("Version check: OK")
        
        # Create output directories
        ensure_output_directories()
        os.makedirs(f'data/output/{version}/localizations', exist_ok=True)

        # Process verticals
        logger.info("Step 2: Verticals")
        verticals_data = scripts.utils.process_step(
            "verticals",
            scripts.verticals.extract_verticals,
            write_verticals,
            f'data/input/{version}/dist/{source_language_code}/categories.json'
        )
        logger.info("Verticals: OK")

        # Process categories
        logger.info("Step 3: Categories")
        categories_data = scripts.utils.process_step(
            "categories",
            scripts.categories.extract_categories,
            write_categories,
            f'data/input/{version}/dist/{source_language_code}/categories.json',
            scripts.categories.load_vertical_ids(version)
        )
        logger.info("Categories: OK")

        # Process attributes
        logger.info("Step 4: Attributes")
        attributes_data = scripts.utils.process_step(
            "attributes",
            scripts.attributes.extract_attributes_and_extended,
            write_attributes,
            f'data/input/{version}/dist/{source_language_code}/attributes.json'
        )
        logger.info("Attributes: OK")

        # Process attribute values
        logger.info("Step 5: Attribute values")
        attribute_values_data = scripts.utils.process_step(
            "attribute values",
            scripts.attribute_values.extract_attribute_values,
            write_attribute_values,
            f'data/input/{version}/dist/{source_language_code}/attribute_values.json'
        )
        logger.info("Attribute values: OK")

        # Process mappings
        logger.info("Step 6: Mappings")
        mappings_data = scripts.utils.process_step(
            "mappings",
            scripts.mappings.create_attribute_value_mappings,
            write_mappings,
            f'data/input/{version}/dist/{source_language_code}/attributes.json',
            scripts.mappings.load_attribute_ids(version),
            scripts.mappings.load_attribute_value_ids(version)
        )
        logger.info("Mappings: OK")

        # Process category-attribute mappings
        logger.info("Step 7: Category-attribute mappings")
        category_attribute_mappings_data = scripts.utils.process_step(
            "category-attribute mappings",
            scripts.mappings.create_category_attribute_mappings,
            write_category_attribute_mappings,
            f'data/input/{version}/dist/{source_language_code}/categories.json',
            scripts.mappings.load_category_ids(version),
            scripts.mappings.load_attribute_ids(version),
            scripts.mappings.load_extended_attribute_ids(version)
        )
        logger.info("Category-attribute mappings: OK")

        # Process attribute-extended attribute mappings
        logger.info("Step 8: Attribute-extended attribute mappings")
        attribute_extended_mappings_data = scripts.utils.process_step(
            "attribute-extended attribute mappings",
            scripts.mappings.create_attribute_extended_mappings,
            write_attribute_extended_mappings,
            f'data/input/{version}/dist/{source_language_code}/attributes.json',
            scripts.mappings.load_attribute_ids(version),
            scripts.mappings.load_extended_attribute_ids(version)
        )
        logger.info("Attribute-extended attribute mappings: OK")

        # Check for duplicates in mapping files
        logger.info("Step 9: Checking for duplicates")
        mapping_files = [
            f'data/output/{version}/attribute_value_mappings.csv',
            f'data/output/{version}/category_attribute_mappings.csv',
            f'data/output/{version}/attribute_extended_mappings.csv'
        ]
        
        for file_path in mapping_files:
            check_and_remove_duplicates(file_path)
        logger.info("Checking for duplicates: OK")

        # Process category localizations
        logger.info("Step 10: Category localizations")
        category_localizations_data = scripts.utils.process_step(
            "category localizations",
            lambda yaml_dir, id_loader: extract_all_localizations('category', f'data/input/{version}/dist', id_loader),
            lambda data: write_localizations(data, 'category'),
            f'data/input/{version}/dist',
            scripts.localizations.load_category_ids
        )
        logger.info("Category localizations: OK")

        # Process attribute localizations
        logger.info("Step 11: Attribute localizations")
        attribute_localizations_data = scripts.utils.process_step(
            "attribute localizations",
            lambda yaml_dir, id_loader: extract_all_localizations('attribute', f'data/input/{version}/dist', id_loader),
            lambda data: write_localizations(data, 'attribute'),
            f'data/input/{version}/dist',
            scripts.localizations.load_attribute_ids
        )
        logger.info("Attribute localizations: OK")

        # Process attribute value localizations
        logger.info("Step 12: Attribute value localizations")
        value_localizations_data = scripts.utils.process_step(
            "attribute value localizations",
            lambda yaml_dir, id_loader: extract_all_localizations('value', f'data/input/{version}/dist', id_loader),
            lambda data: write_localizations(data, 'attribute_value'),
            f'data/input/{version}/dist',
            scripts.localizations.load_value_ids
        )
        logger.info("Attribute value localizations: OK")

        # Process vertical localizations
        logger.info("Step 13: Vertical localizations")
        vertical_localizations_data = scripts.utils.process_step(
            "vertical localizations",
            lambda yaml_dir, _: scripts.localizations.extract_all_vertical_localizations(
                f'data/input/{version}/dist',
                language_codes,
                version
            ),
            lambda data: write_localizations(data, 'vertical'),
            f'data/input/{version}/dist',
            lambda x: None  # Dummy loader since we don't need it
        )
        logger.info("Vertical localizations: OK")

        # Process extended attribute localizations
        logger.info("Step 14: Extended attribute localizations")
        extended_attribute_localizations_data = scripts.utils.process_step(
            "extended attribute localizations",
            lambda yaml_dir, _: scripts.localizations.extract_all_extended_attribute_localizations(
                f'data/input/{version}/dist',
                language_codes,
                version
            ),
            lambda data: write_localizations(data, 'extended_attribute'),
            f'data/input/{version}/dist',
            lambda x: None  # Dummy loader since we don't need it
        )
        logger.info("Extended attribute localizations: OK")

        logger.info("All steps completed successfully")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
