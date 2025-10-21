import sqlite3
import os
import json
from flask import g

DATABASE = 'engineering_tools.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables"""
    try:
        conn = get_db_connection()
        
        # Projects table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                client TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
        # Documents table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name TEXT NOT NULL,
                document_type TEXT,
                file_path TEXT,
                version TEXT DEFAULT '1.0',
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        # Document templates table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS document_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                template_type TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # D365 integration settings
        conn.execute('''
            CREATE TABLE IF NOT EXISTS d365_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Engineering calculations results
        conn.execute('''
            CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                calculation_type TEXT NOT NULL,
                input_data TEXT,
                result_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        # Drafting files metadata
        conn.execute('''
            CREATE TABLE IF NOT EXISTS drafting_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                file_name TEXT NOT NULL,
                file_type TEXT,
                file_path TEXT,
                file_size INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        # Job structure settings
        conn.execute('''
            CREATE TABLE IF NOT EXISTS job_structure_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                folder_path TEXT NOT NULL,
                structure_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Naming conditions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS naming_conditions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                condition_type TEXT NOT NULL,
                pattern TEXT NOT NULL,
                replacement TEXT NOT NULL,
                chains TEXT,
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise

def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """Initialize database for Flask app"""
    app.teardown_appcontext(close_db)
    init_database()

# Naming Conditions Database Functions
def save_naming_condition(condition_type, pattern, replacement, chains=None, enabled=True):
    """Save a naming condition to the database"""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            INSERT INTO naming_conditions (condition_type, pattern, replacement, chains, enabled)
            VALUES (?, ?, ?, ?, ?)
        ''', (condition_type, pattern, replacement, json.dumps(chains) if chains else None, enabled))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error saving naming condition: {e}")
        return None
    finally:
        conn.close()

def get_naming_conditions():
    """Get all naming conditions from the database"""
    conn = get_db_connection()
    try:
        conditions = conn.execute('''
            SELECT id, condition_type, pattern, replacement, chains, enabled, created_at
            FROM naming_conditions
            ORDER BY created_at DESC
        ''').fetchall()
        
        result = []
        for condition in conditions:
            condition_dict = {
                'id': condition['id'],
                'type': condition['condition_type'],
                'pattern': condition['pattern'],
                'replacement': condition['replacement'],
                'enabled': bool(condition['enabled']),
                'created_at': condition['created_at']
            }
            
            if condition['chains']:
                try:
                    condition_dict['chains'] = json.loads(condition['chains'])
                except:
                    condition_dict['chains'] = []
            else:
                condition_dict['chains'] = []
            
            result.append(condition_dict)
        
        return result
    except Exception as e:
        print(f"Error getting naming conditions: {e}")
        return []
    finally:
        conn.close()

def update_naming_condition(condition_id, condition_type=None, pattern=None, replacement=None, chains=None, enabled=None):
    """Update a naming condition in the database"""
    conn = get_db_connection()
    try:
        updates = []
        params = []
        
        if condition_type is not None:
            updates.append("condition_type = ?")
            params.append(condition_type)
        
        if pattern is not None:
            updates.append("pattern = ?")
            params.append(pattern)
        
        if replacement is not None:
            updates.append("replacement = ?")
            params.append(replacement)
        
        if chains is not None:
            updates.append("chains = ?")
            params.append(json.dumps(chains))
        
        if enabled is not None:
            updates.append("enabled = ?")
            params.append(enabled)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(condition_id)
            
            query = f"UPDATE naming_conditions SET {', '.join(updates)} WHERE id = ?"
            conn.execute(query, params)
            conn.commit()
            return True
        
        return False
    except Exception as e:
        print(f"Error updating naming condition: {e}")
        return False
    finally:
        conn.close()

def delete_naming_condition(condition_id):
    """Delete a naming condition from the database"""
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM naming_conditions WHERE id = ?', (condition_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting naming condition: {e}")
        return False
    finally:
        conn.close()

def apply_naming_conditions_to_structure(structure_data, conditions):
    """Apply naming conditions to structure data"""
    import re
    
    def apply_condition_to_item(item, condition):
        """Apply a single condition to an item"""
        name = item['name']
        pattern = condition['pattern']
        replacement = condition['replacement']
        condition_type = condition['type']
        chains = condition.get('chains', [])
        
        # Check if condition matches (including chains)
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
        elif condition_type == 'intuitive':
            # Convert intuitive patterns to regex and test
            intuitive_regex = convert_intuitive_pattern(pattern)
            return bool(intuitive_regex.search(name))
        elif condition_type == 'extract_job_number':
            return bool(re.search(r'\d{5}', name))
        elif condition_type == 'extract_customer':
            return bool(re.search(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', name))
        elif condition_type == 'extract_date':
            return bool(re.search(r'\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{4}[/\-]\d{1,2}[/\-]\d{1,2}', name))
        else:
            return pattern in name
    
    def convert_intuitive_pattern(pattern):
        """Convert intuitive patterns to regex"""
        regex_pattern = pattern
        regex_pattern = re.sub(r'\{d(\d+)\}', r'(\\d{\1})', regex_pattern)
        regex_pattern = re.sub(r'\{customer\}', r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', regex_pattern)
        regex_pattern = re.sub(r'\{date\}', r'(\\d{1,2}[/\\-]\\d{1,2}[/\\-]\\d{2,4}|\\d{4}[/\\-]\\d{1,2}[/\\-]\\d{1,2})', regex_pattern)
        regex_pattern = re.sub(r'\{word\}', r'(\\w+)', regex_pattern)
        regex_pattern = re.sub(r'\{text\}', r'(.+)', regex_pattern)
        return re.compile(regex_pattern)
    
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
        elif condition_type == 'intuitive':
            return apply_intuitive_replacement(name, pattern, replacement)
        elif condition_type == 'extract_job_number':
            job_match = re.search(r'\d{5}', name)
            if job_match:
                return replacement.replace('$1', job_match.group(0))
            return name
        elif condition_type == 'extract_customer':
            customer_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', name)
            if customer_match:
                return replacement.replace('$1', customer_match.group(1))
            return name
        elif condition_type == 'extract_date':
            date_match = re.search(r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{4}[/\-]\d{1,2}[/\-]\d{1,2})', name)
            if date_match:
                return replacement.replace('$1', date_match.group(1))
            return name
        else:
            return name.replace(pattern, replacement)
    
    def apply_intuitive_replacement(name, pattern, replacement):
        """Apply intuitive pattern replacement"""
        regex_pattern = pattern
        captures = []
        
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
                
                for i, capture in enumerate(captures):
                    value = match.group(i + 1)
                    
                    if capture['type'] == 'digits':
                        result = re.sub(f"\\{{{capture['count']}\\}}", value, result)
                    else:
                        result = re.sub(f"\\{{{capture['type']}\\}}", value, result)
                
                return result
        except re.error as e:
            print(f'Invalid intuitive pattern: {pattern} - {e}')
        
        return name
    
    # Apply conditions to each item in the structure
    for item in structure_data:
        for condition in conditions:
            if condition.get('enabled', True):
                new_alias = apply_condition_to_item(item, condition)
                if new_alias != item['name']:
                    item['alias'] = new_alias
    
    return structure_data
