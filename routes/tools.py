from flask import Blueprint, render_template, request, jsonify

tools_bp = Blueprint('tools', __name__)

@tools_bp.route('/')
def tools_home():
    return render_template('tools/index.html')

@tools_bp.route('/converters')
def converters():
    return render_template('tools/converters.html')

@tools_bp.route('/calculators')
def calculators():
    return render_template('tools/calculators.html')

@tools_bp.route('/api/convert', methods=['POST'])
def convert_units():
    data = request.get_json()
    # Placeholder for unit conversion logic
    return jsonify({
        'converted_value': data.get('value', 0),
        'unit': data.get('to_unit', '')
    })
