from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
import uuid
import logging
import pandas as pd
import traceback

from backend.utils.csv_parser import parse_csv
from backend.utils.data_transform import transform_data
from backend.utils.db_client import insert_fitness_data

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__, url_prefix='/api')

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle CSV file upload from MyFitnessPal exports.
    Process, validate, and store the data in PostgreSQL.
    Supports multiple users with complex JSON-formatted nutrition data.
    """
    if 'file' not in request.files:
        logger.warning("No file part in the request")
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning("No file selected")
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        try:
            try:
                preview_df = pd.read_csv(file_path, nrows=5)
                if preview_df.empty:
                    raise ValueError("The CSV file is empty")
                
                if len(preview_df.columns) < 3:
                    raise ValueError("CSV does not have enough columns. Expected at least 3 columns including user_id, date, and nutrition data.")
                
                logger.info(f"Valid CSV format detected with {len(preview_df.columns)} columns")
            except pd.errors.EmptyDataError:
                raise ValueError("The CSV file is empty")
            except pd.errors.ParserError:
                raise ValueError("Invalid CSV format. Please check the file and try again.")
            
            logger.info(f"Parsing CSV file: {original_filename}")
            parsed_data = parse_csv(file_path)
            
            if parsed_data.empty:
                raise ValueError("No valid data found in the CSV file after parsing")
            
            unique_users = parsed_data['user_id'].unique()
            logger.info(f"Found data for {len(unique_users)} user(s): {', '.join(map(str, unique_users))}")
            
            logger.info("Transforming data")
            transformed_data = transform_data(parsed_data)
            
            logger.info("Inserting data into database")
            rows_affected = insert_fitness_data(transformed_data)
            
            os.remove(file_path)
            
            user_summary = ""
            if len(unique_users) == 1:
                user_summary = f"Data for user ID {unique_users[0]} processed successfully."
            else:
                user_summary = f"Data for {len(unique_users)} users processed successfully."
            
            return jsonify({
                'success': True,
                'message': f'File uploaded and processed successfully. {rows_affected} records inserted. {user_summary}',
                'filename': original_filename,
                'users_processed': len(unique_users),
                'users_processed_details': unique_users.tolist(),  
                'records_inserted': rows_affected
            }), 200
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return jsonify({
                'error': f'Validation error: {str(e)}'
            }), 400
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            logger.error(traceback.format_exc())
            
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return jsonify({
                'error': f'Error processing file: {str(e)}'
            }), 500
    
    logger.warning(f"File type not allowed: {file.filename}")
    return jsonify({'error': 'File type not allowed. Please upload a CSV file.'}), 400 