from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import sys
from database import init_app as init_database

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['DATABASE'] = 'engineering_tools.db'
    
    # Enable CORS for Electron
    CORS(app)
    
    # Initialize database
    try:
        init_database(app)
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        print("App will continue without database features")
    
    # Register blueprints
    from routes.main import main_bp
    from routes.drafting import drafting_bp
    from routes.engineering import engineering_bp
    from routes.tools import tools_bp
    from routes.d365 import d365_bp
    from routes.job_docs import job_docs_bp
    from routes.job_structure import job_structure_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(drafting_bp, url_prefix='/drafting')
    app.register_blueprint(engineering_bp, url_prefix='/engineering')
    app.register_blueprint(tools_bp, url_prefix='/tools')
    app.register_blueprint(d365_bp, url_prefix='/d365')
    app.register_blueprint(job_docs_bp, url_prefix='/job-docs')
    app.register_blueprint(job_structure_bp, url_prefix='/job-structure')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
