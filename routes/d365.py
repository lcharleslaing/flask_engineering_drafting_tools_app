from flask import Blueprint, render_template, request, jsonify

d365_bp = Blueprint('d365', __name__)

@d365_bp.route('/')
def d365_home():
    return render_template('d365/index.html')

@d365_bp.route('/integration')
def integration():
    return render_template('d365/integration.html')

@d365_bp.route('/data-sync')
def data_sync():
    return render_template('d365/data_sync.html')

@d365_bp.route('/api/status')
def integration_status():
    return jsonify({
        'status': 'ready',
        'connection': 'not_configured',
        'last_sync': None
    })
