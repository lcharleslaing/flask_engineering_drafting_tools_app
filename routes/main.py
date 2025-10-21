from flask import Blueprint, render_template, request, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/api/status')
def status():
    return jsonify({
        'status': 'running',
        'app': 'Engineering/Drafting Tools',
        'version': '1.0.0'
    })
