import csv
import os
import logging

def write_csv(data, fieldnames, output_file):
    """Write data to a CSV file with the given fieldnames."""
    # Extract version from output_file path (data/output/version/filename.csv)
    version = output_file.split('/')[2]
    output_dir = f'data/output/{version}'
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def process_step(step_name, extract_func, write_func, *args):
    """Process a single step in the pipeline."""
    try:
        data = extract_func(*args)
        write_func(data)
        return data
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error processing {step_name}: {str(e)}")
        raise 