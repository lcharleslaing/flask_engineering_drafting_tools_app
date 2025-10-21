#!/usr/bin/env python3
"""
Customer Job Structure Scanner
Scans a customer folder and returns a structured representation of all files and folders.
"""

import os
import json
from datetime import datetime
from pathlib import Path

def scan_customer_folder(folder_path, naming_conditions=None):
    """
    Scan a customer folder and return structured data
    
    Args:
        folder_path (str): Path to the customer folder to scan
        naming_conditions (list): List of naming condition dictionaries
        
    Returns:
        list: List of dictionaries containing file/folder information
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder path does not exist: {folder_path}")
    
    if naming_conditions is None:
        naming_conditions = []
    
    structure = []
    
    def apply_naming_conditions(name, conditions):
        """Apply naming conditions to a name"""
        import re
        
        for condition in conditions:
            if not condition.get('enabled', True):
                continue
                
            pattern = condition['pattern']
            replacement = condition['replacement']
            condition_type = condition.get('type', 'contains')
            chains = condition.get('chains', [])
            
            if matches_condition_with_chains(name, pattern, condition_type, chains):
                return apply_replacement(name, pattern, replacement, condition_type)
        
        return name
    
    def matches_condition_with_chains(name, pattern, condition_type, chains):
        """Check if a name matches a condition with chained conditions"""
        # Check main condition
        main_match = matches_condition(name, pattern, condition_type)
        
        # If no chains, return main match
        if not chains:
            return main_match
        
        # Evaluate chains
        result = main_match
        
        for chain in chains:
            chain_match = matches_condition(name, chain['pattern'], chain['type'])
            operator = chain.get('operator', 'AND')
            
            if operator == 'AND':
                result = result and chain_match
            elif operator == 'OR':
                result = result or chain_match
        
        return result
    
    def matches_condition(name, pattern, condition_type):
        """Check if a name matches a condition"""
        if condition_type == 'contains':
            return pattern in name
        elif condition_type == 'startswith':
            return name.startswith(pattern)
        elif condition_type == 'endswith':
            return name.endswith(pattern)
        elif condition_type == 'equals':
            return name == pattern
        elif condition_type == 'regex':
            try:
                return bool(re.search(pattern, name))
            except re.error:
                return False
        elif condition_type == 'extract_job_number':
            # Look for 5-digit numbers
            return bool(re.search(r'\d{5}', name))
        elif condition_type == 'extract_customer':
            # Look for common customer name patterns
            return bool(re.search(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', name))
        elif condition_type == 'extract_date':
            # Look for date patterns (MM/DD/YYYY, YYYY-MM-DD, etc.)
            return bool(re.search(r'\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{4}[/\-]\d{1,2}[/\-]\d{1,2}', name))
        elif condition_type == 'intuitive':
            # Convert intuitive patterns to regex and test
            intuitive_regex = convert_intuitive_pattern(pattern)
            return bool(intuitive_regex.search(name))
        elif condition_type == 'not_contains':
            return pattern not in name
        elif condition_type == 'not_startswith':
            return not name.startswith(pattern)
        elif condition_type == 'not_endswith':
            return not name.endswith(pattern)
        elif condition_type == 'not_equals':
            return name != pattern
        else:
            return pattern in name
    
    def apply_replacement(name, pattern, replacement, condition_type):
        """Apply replacement based on condition type"""
        if condition_type == 'contains':
            return name.replace(pattern, replacement)
        elif condition_type == 'startswith':
            return name.replace(pattern, replacement) if name.startswith(pattern) else name
        elif condition_type == 'endswith':
            return name.replace(pattern, replacement) if name.endswith(pattern) else name
        elif condition_type == 'equals':
            return replacement
        elif condition_type == 'regex':
            try:
                return re.sub(pattern, replacement, name)
            except re.error:
                return name
        elif condition_type == 'extract_job_number':
            # Extract 5-digit job number and use in replacement
            job_match = re.search(r'\d{5}', name)
            if job_match:
                return replacement.replace('$1', job_match.group(0))
            return name
        elif condition_type == 'extract_customer':
            # Extract customer name and use in replacement
            customer_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', name)
            if customer_match:
                return replacement.replace('$1', customer_match.group(1))
            return name
        elif condition_type == 'extract_date':
            # Extract date and use in replacement
            date_match = re.search(r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{4}[/\-]\d{1,2}[/\-]\d{1,2})', name)
            if date_match:
                return replacement.replace('$1', date_match.group(1))
            return name
        elif condition_type == 'intuitive':
            # Apply intuitive pattern replacement
            return apply_intuitive_replacement(name, pattern, replacement)
        elif condition_type in ['not_contains', 'not_startswith', 'not_endswith', 'not_equals']:
            return replacement  # For "not" conditions, just use the replacement
        else:
            return name.replace(pattern, replacement)
    
    def convert_intuitive_pattern(pattern):
        """Convert intuitive patterns to regex"""
        regex_pattern = pattern
        
        # Convert intuitive syntax to regex
        regex_pattern = re.sub(r'\{d(\d+)\}', r'(\\d{\1})', regex_pattern)  # {d5} -> (\d{5})
        regex_pattern = re.sub(r'\{customer\}', r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', regex_pattern)  # {customer} -> customer name pattern
        regex_pattern = re.sub(r'\{date\}', r'(\\d{1,2}[/\\-]\\d{1,2}[/\\-]\\d{2,4}|\\d{4}[/\\-]\\d{1,2}[/\\-]\\d{1,2})', regex_pattern)  # {date} -> date pattern
        regex_pattern = re.sub(r'\{word\}', r'(\\w+)', regex_pattern)  # {word} -> any word
        regex_pattern = re.sub(r'\{text\}', r'(.+)', regex_pattern)  # {text} -> any text
        
        return re.compile(regex_pattern)
    
    def apply_intuitive_replacement(name, pattern, replacement):
        """Apply intuitive pattern replacement"""
        regex_pattern = pattern
        captures = []
        
        # Convert pattern and collect capture groups
        def replace_digits(match):
            digits = int(match.group(1))
            captures.append({'type': 'digits', 'count': digits})
            return f'(\\d{{{digits}}})'
        
        def replace_customer(match):
            captures.append({'type': 'customer'})
            return '([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)'
        
        def replace_date(match):
            captures.append({'type': 'date'})
            return '(\\d{1,2}[/\\-]\\d{1,2}[/\\-]\\d{2,4}|\\d{4}[/\\-]\\d{1,2}[/\\-]\\d{1,2})'
        
        def replace_word(match):
            captures.append({'type': 'word'})
            return '(\\w+)'
        
        def replace_text(match):
            captures.append({'type': 'text'})
            return '(.+)'
        
        regex_pattern = re.sub(r'\{d(\d+)\}', replace_digits, regex_pattern)
        regex_pattern = re.sub(r'\{customer\}', replace_customer, regex_pattern)
        regex_pattern = re.sub(r'\{date\}', replace_date, regex_pattern)
        regex_pattern = re.sub(r'\{word\}', replace_word, regex_pattern)
        regex_pattern = re.sub(r'\{text\}', replace_text, regex_pattern)
        
        try:
            regex = re.compile(regex_pattern)
            match = regex.search(name)
            
            if match:
                result = replacement
                
                # Replace {5}, {customer}, etc. with actual values
                for i, capture in enumerate(captures):
                    value = match.group(i + 1)  # match.group(0) is full match
                    
                    if capture['type'] == 'digits':
                        result = re.sub(f"\\{{{capture['count']}\\}}", value, result)
                    else:
                        result = re.sub(f"\\{{{capture['type']}\\}}", value, result)
                
                return result
        except re.error as e:
            print(f'Invalid intuitive pattern: {pattern} - {e}')
        
        return name
    
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
                    alias = apply_naming_conditions(item, naming_conditions)
                    folder_info = {
                        'type': 'folder',
                        'name': item,
                        'path': item_relative_path,
                        'full_path': item_path,
                        'included': True,  # Default to included
                        'alias': alias,  # Apply naming conditions
                        'applications': '',  # Empty by default
                        'children': []
                    }
                    structure.append(folder_info)
                    
                    # Recursively scan subdirectory
                    scan_directory(item_path, item_relative_path)
                    
                else:
                    # It's a file
                    file_name, file_ext = os.path.splitext(item)
                    alias = apply_naming_conditions(file_name, naming_conditions)
                    file_info = {
                        'type': 'file',
                        'name': item,
                        'file_name': file_name,
                        'file_extension': file_ext,
                        'path': item_relative_path,
                        'full_path': item_path,
                        'included': True,  # Default to included
                        'alias': alias,  # Apply naming conditions
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
