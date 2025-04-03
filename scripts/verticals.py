import json

def extract_verticals(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    verticals = data.get('verticals', [])

    extracted_info = []
    for i, vertical in enumerate(verticals, 1):
        name = vertical.get('name')
        prefix = vertical.get('prefix')
        extracted_info.append({'id': i, 'name': name, 'prefix': prefix})

    return extracted_info