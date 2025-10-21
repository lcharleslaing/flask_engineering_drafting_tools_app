from flask import Blueprint, render_template, request, jsonify

drafting_bp = Blueprint('drafting', __name__)

@drafting_bp.route('/')
def drafting_home():
    return render_template('drafting/index.html')

@drafting_bp.route('/cad')
def cad_tools():
    return render_template('drafting/cad.html')

@drafting_bp.route('/blueprints')
def blueprints():
    return render_template('drafting/blueprints.html')

@drafting_bp.route('/api/projects')
def get_projects():
    # Placeholder for projects API
    return jsonify({
        'projects': [
            {'id': 1, 'name': 'Sample Project 1', 'status': 'active'},
            {'id': 2, 'name': 'Sample Project 2', 'status': 'draft'}
        ]
    })
