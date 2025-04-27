#!/usr/bin/env python3
"""
JSON to CSV Converter for Nigerian Soil Science Journal Articles Metadata

This script converts a JSON file containing academic journal metadata into a CSV file
with columns arranged in a specific order. The script handles proper CSV formatting
including escaping quotes and commas within fields.

Usage:
    python json_to_csv_converter.py input.json output.csv

Author: Engr. Salisu Zubairu Gaya
Date: April 25, 2025
"""

import json
import csv
import sys
import os
import argparse


def convert_json_to_csv(input_file, output_file, column_order=None):
    """
    Convert JSON metadata to CSV with specified column order.
    
    Args:
        input_file (str): Path to the input JSON file
        output_file (str): Path to the output CSV file
        column_order (list, optional): List of columns in the desired order.
            Defaults to ['title', 'authors', 'abstract', 'keywords', 'email', 'page_number', 'file_path']
    
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    if column_order is None:
        column_order = ['title', 'authors', 'abstract', 'keywords', 'email', 'page_number', 'file_path']
    
    try:
        # Read the JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON file: {e}")
                return False
        
        # Validate JSON structure
        if not isinstance(data, list):
            print("Error: JSON file must contain a list of objects")
            return False
        
        for item in data:
            if not isinstance(item, dict):
                print("Error: Each item in the JSON list must be an object")
                return False
        
        # Check for required fields
        missing_fields = []
        for i, item in enumerate(data):
            for field in column_order:
                if field not in item:
                    missing_fields.append((i, field))
        
        if missing_fields:
            print("Warning: Some required fields are missing:")
            for i, field in missing_fields:
                print(f"  Item {i}: Missing field '{field}'")
            
            response = input("Do you want to continue anyway? (y/n): ")
            if response.lower() != 'y':
                return False
        
        # Write to CSV file
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            
            # Write header
            writer.writerow(column_order)
            
            # Write data rows
            for item in data:
                row = []
                for column in column_order:
                    # Get the value or empty string if not present
                    value = item.get(column, "")
                    row.append(value)
                writer.writerow(row)
        
        print(f"Successfully converted {len(data)} records from '{input_file}' to '{output_file}'")
        return True
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


def main():
    """Main function to parse arguments and call the converter."""
    parser = argparse.ArgumentParser(description='Convert journal metadata from JSON to CSV format.')
    parser.add_argument('input_file', help='Path to the input JSON file')
    parser.add_argument('output_file', help='Path to the output CSV file')
    parser.add_argument('--columns', help='Comma-separated list of columns in desired order')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.isfile(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist")
        return 1
    
    # Parse column order if provided
    column_order = None
    if args.columns:
        column_order = [col.strip() for col in args.columns.split(',')]
    
    # Convert JSON to CSV
    success = convert_json_to_csv(args.input_file, args.output_file, column_order)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())