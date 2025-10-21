#!/usr/bin/env python3
"""
Customer Job Structure Scanner
Scans a customer folder and returns a structured representation of all files and folders.
"""

import os
import json
from datetime import datetime
from pathlib import Path

def scan_customer_folder(folder_path):
    """
    Scan a customer folder and return structured data
    
    Args:
        folder_path (str): Path to the customer folder to scan
        
    Returns:
        list: List of dictionaries containing file/folder information
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder path does not exist: {folder_path}")
    
    structure = []
    
    def scan_directory(current_path, relative_path=""):
        """Recursively scan directory structure"""
        try:
            # Get all items in current directory
            items = os.listdir(current_path)
            items.sort()  # Sort alphabetically for consistent ordering
            
            for item in items:
                item_path = os.path.join(current_path, item)
                item_relative_path = os.path.join(relative_path, item) if relative_path else item
                
                if os.path.isdir(item_path):
                    # It's a directory
                    folder_info = {
                        'type': 'folder',
                        'name': item,
                        'path': item_relative_path,
                        'full_path': item_path,
                        'included': True,  # Default to included
                        'alias': item,  # Default alias is the folder name
                        'applications': '',  # Empty by default
                        'children': []
                    }
                    structure.append(folder_info)
                    
                    # Recursively scan subdirectory
                    scan_directory(item_path, item_relative_path)
                    
                else:
                    # It's a file
                    file_name, file_ext = os.path.splitext(item)
                    file_info = {
                        'type': 'file',
                        'name': item,
                        'file_name': file_name,
                        'file_extension': file_ext,
                        'path': item_relative_path,
                        'full_path': item_path,
                        'included': True,  # Default to included
                        'alias': file_name,  # Default alias is filename without extension
                        'applications': '',  # Empty by default
                        'size': os.path.getsize(item_path)
                    }
                    structure.append(file_info)
                    
        except PermissionError:
            print(f"Permission denied accessing: {current_path}")
        except Exception as e:
            print(f"Error scanning {current_path}: {e}")
    
    # Start scanning from the root folder
    scan_directory(folder_path)
    
    return structure

def save_structure_to_json(structure, output_file):
    """
    Save structure data to a JSON file
    
    Args:
        structure (list): Structure data to save
        output_file (str): Path to output JSON file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)

def main():
    """Main function for command line usage"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python get_customer_job_structure.py <folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    
    try:
        print(f"Scanning folder: {folder_path}")
        structure = scan_customer_folder(folder_path)
        
        # Create output filename based on folder name
        folder_name = os.path.basename(folder_path)
        output_file = f"{folder_name}_structure.json"
        
        # Save to JSON file
        save_structure_to_json(structure, output_file)
        
        print(f"Scan complete! Found {len(structure)} items.")
        print(f"Structure saved to: {output_file}")
        
        # Print summary
        folders = [item for item in structure if item['type'] == 'folder']
        files = [item for item in structure if item['type'] == 'file']
        
        print(f"Folders: {len(folders)}")
        print(f"Files: {len(files)}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
