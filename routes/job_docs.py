from flask import Blueprint, render_template, request, jsonify

def get_db_connection():
    """Get database connection - imported locally to avoid circular imports"""
    from database import get_db_connection as _get_db_connection
    return _get_db_connection()

job_docs_bp = Blueprint('job_docs', __name__)

@job_docs_bp.route('/')
def job_docs_home():
    return render_template('job_docs/index.html')

@job_docs_bp.route('/projects')
def projects():
    return render_template('job_docs/projects.html')

@job_docs_bp.route('/documents')
def documents():
    return render_template('job_docs/documents.html')

@job_docs_bp.route('/templates')
def templates():
    return render_template('job_docs/templates.html')

@job_docs_bp.route('/api/projects')
def get_projects():
    conn = get_db_connection()
    projects = conn.execute(
        'SELECT * FROM projects ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    
    return jsonify([dict(project) for project in projects])

@job_docs_bp.route('/api/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute(
        'INSERT INTO projects (name, description, status, client) VALUES (?, ?, ?, ?)',
        (data['name'], data['description'], data.get('status', 'active'), data.get('client', ''))
    )
    conn.commit()
    project_id = conn.lastrowid
    conn.close()
    
    return jsonify({'id': project_id, 'message': 'Project created successfully'})

@job_docs_bp.route('/api/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute(
        'UPDATE projects SET name = ?, description = ?, status = ?, client = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (data['name'], data['description'], data['status'], data.get('client', ''), project_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Project updated successfully'})

@job_docs_bp.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Project deleted successfully'})
