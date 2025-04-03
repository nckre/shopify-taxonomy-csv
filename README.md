# Shopify Taxonomy to .csv for SQL databases

## Purpose

This script is turning the shopify taxonomy into a `.csv` format with mappings that can be used for SQL databases.
For each type (vertical, category, attribute, attribute value, extended attribute) there is a `.csv` file with the English translations. Each file has an additional `localizations_XX.csv` that includes all the languages codes specified in the `main.py` script.

## How to use

1. Drop the latest distribution from [Shopify/product-taxonomy/tree/main/dist](https://github.com/Shopify/product-taxonomy/tree/main/dist) into `data/input/{version_name}` where `version_name` is the version from `taxonomy.json` (e.g. `2025-06-unstable`).
2. Update the version in `main.py` and specify the target languages for localization.
3. Run the script and see the output files in `data/output/{version_name}`.

## What does the script do?

It uses different `.json` files from the shopify dist folder as input to create `.csv` files with a serial `id` in addition to the shopify `gid` indentifier. These `id` are used to create `_mappings.csv` files that can be used for junction tables.
The script uses `.txt` files (where available) for translations since the structure is simpler. Since verticals and extended attributes don't have `.txt` files, these translations come from the `.json` files instead.
