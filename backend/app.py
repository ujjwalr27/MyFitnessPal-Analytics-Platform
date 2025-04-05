from flask import Flask, render_template, request, jsonify, redirect
from flask_cors import CORS
import os
import sys
from werkzeug.utils import secure_filename

# Add the parent directory to sys.path to make imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import custom modules
from backend.utils.csv_parser import parse_csv
from backend.utils.data_transform import transform_data
from backend.utils.db_client import insert_fitness_data, init_db
from backend.config import Config

app = Flask(__name__, 
            static_folder="../frontend/static",
            template_folder="../frontend/templates")
app.config.from_object(Config)
CORS(app)

# Initialize database on startup
with app.app_context():
    init_db()

# Import routes (must be after app initialization)
from backend.routes.upload import upload_bp

# Register blueprints
app.register_blueprint(upload_bp)

@app.route('/')
def index():
    """Render the main upload page."""
    return render_template('index.html')

@app.route('/grafana')
def grafana_redirect():
    """Redirect to the Grafana dashboard."""
    return redirect('http://localhost:3001')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 