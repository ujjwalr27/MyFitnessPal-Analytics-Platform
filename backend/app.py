from flask import Flask, render_template, request, jsonify, redirect
from flask_cors import CORS
import os
import sys
from werkzeug.utils import secure_filename

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.utils.csv_parser import parse_csv
from backend.utils.data_transform import transform_data
from backend.utils.db_client import insert_fitness_data, init_db
from backend.config import Config

app = Flask(__name__, 
            static_folder="../frontend/static",
            template_folder="../frontend/templates")
app.config.from_object(Config)
CORS(app)

with app.app_context():
    init_db()

from backend.routes.upload import upload_bp

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