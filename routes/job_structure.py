from flask import Blueprint, render_template, request, jsonify
import os
import json
import re
from datetime import datetime

def generateSmartAlias(filename):
    """Generate a smart alias for a filename by removing common patterns"""
    # Remove common patterns
    # Remove job numbers at the start (e.g., "35394-R1 FLOW" -> "FLOW")
    alias = re.sub(r'^\d+[-\s]*[A-Z]*[-\s]*', '', filename)
    # Remove revision numbers (e.g., "FLOW-R1" -> "FLOW")
    alias = re.sub(r'[-\s]*R\d+', '', alias)
    # Clean up extra spaces
    alias = re.sub(r'\s+', ' ', alias).strip()
    
    # If alias is empty after cleaning, use the original filename
    if not alias:
        alias = filename
    
    return alias

def get_db_connection():
    """Get database connection - imported locally to avoid circular imports"""
    from database import get_db_connection as _get_db_connection
    return _get_db_connection()

job_structure_bp = Blueprint('job_structure', __name__)

@job_structure_bp.route('/')
def job_structure_home():
    return render_template('job_structure/index.html')

@job_structure_bp.route('/api/scan-folder', methods=['POST'])
def scan_folder():
    """Scan a folder and return its structure"""
    data = request.get_json()
    folder_path = data.get('folder_path')
    customer_name = data.get('customer_name', 'Unknown')
    
    if not folder_path:
        return jsonify({'error': 'No folder path provided'}), 400
    
    # Strip quotes and normalize the path
    folder_path = folder_path.strip('"\'')
    folder_path = os.path.normpath(folder_path)
    
    if not os.path.exists(folder_path):
        return jsonify({'error': f'Folder does not exist: {folder_path}'}), 400
    
    if not os.path.isdir(folder_path):
        return jsonify({'error': f'Path is not a directory: {folder_path}'}), 400
    
    try:
        # Check if structure already exists for this customer and folder
        conn = get_db_connection()
        existing = conn.execute(
            'SELECT id FROM job_structure_settings WHERE customer_name = ? AND folder_path = ?',
            (customer_name, folder_path)
        ).fetchone()
        
        if existing:
            conn.close()
            return jsonify({'error': f'Structure already exists for {customer_name} at {folder_path}. Please delete the existing structure first.'}), 400
        
        # Call the Python script to scan the folder
        structure = scan_directory_structure(folder_path)
        
        # Save to database
        conn.execute(
            'INSERT INTO job_structure_settings (customer_name, folder_path, structure_data, created_at) VALUES (?, ?, ?, ?)',
            (customer_name, folder_path, json.dumps(structure), datetime.now())
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'structure': structure})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_structure_bp.route('/api/update-item', methods=['POST'])
def update_item():
    """Update an item's settings (checkbox, alias, applications)"""
    data = request.get_json()
    
    conn = get_db_connection()
    conn.execute(
        'UPDATE job_structure_settings SET structure_data = ?, updated_at = ? WHERE id = ?',
        (json.dumps(data['structure_data']), datetime.now(), data['structure_id'])
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@job_structure_bp.route('/api/get-structures')
def get_structures():
    """Get all saved structures"""
    conn = get_db_connection()
    structures = conn.execute(
        'SELECT * FROM job_structure_settings ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    
    result = []
    for structure in structures:
        result.append({
            'id': structure['id'],
            'customer_name': structure['customer_name'],
            'folder_path': structure['folder_path'],
            'structure_data': json.loads(structure['structure_data']),
            'created_at': structure['created_at']
        })
    
    return jsonify(result)

@job_structure_bp.route('/api/delete-structure/<int:structure_id>', methods=['DELETE'])
def delete_structure(structure_id):
    """Delete a job structure"""
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM job_structure_settings WHERE id = ?', (structure_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Structure deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def scan_directory_structure(root_path):
    """Scan directory structure and return organized data"""
    structure = []
    
    def scan_directory(current_path, relative_path=""):
        try:
            items = os.listdir(current_path)
            items.sort()  # Sort alphabetically
            
            for item in items:
                item_path = os.path.join(current_path, item)
                item_relative_path = os.path.join(relative_path, item) if relative_path else item
                
                if os.path.isdir(item_path):
                    # It's a directory
                    structure.append({
                        'type': 'folder',
                        'name': item,
                        'path': item_relative_path,
                        'full_path': item_path,
                        'included': True,  # Default to included
                        'alias': item,  # Default alias is the name
                        'applications': '',  # Empty by default
                        'collapsed': False,  # Default to expanded
                        'children': []
                    })
                    
                    # Recursively scan subdirectory
                    scan_directory(item_path, item_relative_path)
                else:
                    # It's a file
                    file_name, file_ext = os.path.splitext(item)
                    structure.append({
                        'type': 'file',
                        'name': item,
                        'file_name': file_name,
                        'file_extension': file_ext,
                        'path': item_relative_path,
                        'full_path': item_path,
                        'included': True,  # Default to included
                        'alias': generateSmartAlias(file_name),  # Smart alias generation
                        'applications': '',  # Empty by default
                        'size': os.path.getsize(item_path)
                    })
        except PermissionError:
            pass  # Skip directories we can't access
    
    scan_directory(root_path)
    return structure
