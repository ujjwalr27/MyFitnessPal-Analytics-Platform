import pandas as pd
import numpy as np
import logging
import json
import re

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_csv(file_path):
    """
    Parse a MyFitnessPal CSV export file with complex JSON structure and validate its structure.
    Handles multiple users with their nutrition data.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Parsed and validated dataframe
        
    Raises:
        ValueError: If the CSV is invalid or missing required columns
    """
    try:
        # Try to read the CSV file with pandas
        df = pd.read_csv(file_path)
        
        # Check if the dataframe is empty
        if df.empty:
            raise ValueError("The uploaded CSV file is empty.")
        
        # Check for required columns - the actual structure may vary
        # We expect at least a user ID column, date column, and JSON data
        if len(df.columns) < 3:
            raise ValueError("CSV does not have enough columns. Expected at least 3 columns.")
        
        # Rename columns to standardized names for easier processing
        # Assuming Column1 is user_id, Column2 is date, and the rest contain nutrition data
        column_mapping = {}
        for i, col in enumerate(df.columns):
            if i == 0:
                column_mapping[col] = 'user_id'
            elif i == 1:
                column_mapping[col] = 'date'
            else:
                column_mapping[col] = f'data_{i-1}'
        
        df = df.rename(columns=column_mapping)
        
        # Convert date format - try multiple formats
        try:
            # First, look at the first date to determine format
            date_sample = df['date'].iloc[0] if not df.empty else ""
            
            if re.match(r'^\d{2}-\d{2}-\d{4}$', str(date_sample)):
                # Format: DD-MM-YYYY
                date_format = '%d-%m-%Y'
            elif re.match(r'^\d{4}-\d{2}-\d{2}$', str(date_sample)):
                # Format: YYYY-MM-DD
                date_format = '%Y-%m-%d'
            else:
                # Let pandas infer the format
                date_format = None
                
            if date_format:
                df['date'] = pd.to_datetime(df['date'], format=date_format)
            else:
                df['date'] = pd.to_datetime(df['date'])
                
        except Exception as e:
            logger.warning(f"Date format conversion warning: {str(e)}")
            # Try a more flexible approach
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            # Check if any dates are NaT (Not a Time) after conversion
            if df['date'].isna().any():
                raise ValueError("Could not parse date column. Please check the date format.")
        
        # Process the complex JSON data
        processed_data = []
        
        for _, row in df.iterrows():
            user_id = row['user_id']
            date = row['date']
            
            # Combine all JSON data columns into a single string
            json_data = ""
            for col in df.columns:
                if col.startswith('data_'):
                    if pd.notna(row[col]):
                        json_data += str(row[col])
            
            # Try to parse the combined JSON data
            try:
                # Handle case where JSON might be incomplete or spread across columns
                # Clean up the JSON string if necessary
                json_data = json_data.replace("'", '"')
                
                # Extract nutritional data
                nutrition_data = extract_nutrition_data(json_data, user_id, date)
                processed_data.extend(nutrition_data)
                
            except Exception as e:
                logger.warning(f"Error processing JSON for user {user_id} on {date}: {str(e)}")
                # Add basic record even if JSON parsing fails
                processed_data.append({
                    'user_id': user_id,
                    'date': date,
                    'calories': None,
                    'carbs': None,
                    'fat': None,
                    'protein': None,
                    'sodium': None,
                    'sugar': None
                })
        
        # Create a new dataframe from the processed data
        result_df = pd.DataFrame(processed_data)
        
        logger.info(f"Successfully parsed CSV with {len(result_df)} records.")
        
        return result_df
        
    except pd.errors.ParserError as e:
        logger.error(f"Error parsing CSV: {str(e)}")
        raise ValueError(f"Invalid CSV format: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected error while parsing CSV: {str(e)}")
        raise ValueError(f"Error processing the CSV file: {str(e)}")

def extract_nutrition_data(json_str, user_id, date):
    """
    Extract nutrition data from complex JSON structure.
    
    Args:
        json_str (str): JSON string containing nutrition data
        user_id: User identifier
        date: Date of the record
        
    Returns:
        list: List of dictionaries with extracted nutrition data
    """
    try:
        data = []
        
        # Create initial data structure with empty values
        record = {
            'user_id': user_id,
            'date': date,
            'calories': None,
            'carbs': None,
            'fat': None,
            'protein': None,
            'sodium': None,
            'sugar': None
        }
        
        # First, try to extract values using regex pattern matching
        record['calories'] = extract_value(json_str, 'Calories')
        record['carbs'] = extract_value(json_str, 'Carbs')
        record['fat'] = extract_value(json_str, 'Fat')
        record['protein'] = extract_value(json_str, 'Protein')
        record['sodium'] = extract_value(json_str, 'Sodium')
        record['sugar'] = extract_value(json_str, 'Sugar')
        
        # Only if we couldn't extract values with regex, try JSON parsing
        if record['calories'] is None and record['carbs'] is None:
            try:
                json_data = json.loads(json_str)
                
                # Try to navigate the complex structure if it's a dict
                if isinstance(json_data, dict) and 'meal' in json_data:
                    dishes = json_data.get('dishes', [])
                    for dish in dishes:
                        nutrition = dish.get('nutrition', [])
                        for item in nutrition:
                            name = item.get('name', '').lower()
                            value = item.get('value', 0)
                            
                            if 'calories' in name:
                                record['calories'] = float(value) if value else 0
                            elif 'carbs' in name:
                                record['carbs'] = float(value) if value else 0
                            elif 'fat' in name:
                                record['fat'] = float(value) if value else 0
                            elif 'protein' in name:
                                record['protein'] = float(value) if value else 0
                            elif 'sodium' in name:
                                record['sodium'] = float(value) if value else 0
                            elif 'sugar' in name:
                                record['sugar'] = float(value) if value else 0
            except json.JSONDecodeError:
                # JSON parsing failed, but we already tried regex
                pass
        
        data.append(record)
        return data
        
    except Exception as e:
        logger.error(f"Error extracting nutrition data: {str(e)}")
        # Return a basic record with the user ID and date
        return [{
            'user_id': user_id,
            'date': date,
            'calories': None,
            'carbs': None,
            'fat': None,
            'protein': None,
            'sodium': None,
            'sugar': None
        }]

def extract_value(json_str, nutrient_name):
    """
    Extract a nutrient value from a JSON string using string manipulation.
    Used as a fallback when JSON parsing fails.
    
    Args:
        json_str (str): JSON string to extract from
        nutrient_name (str): Name of the nutrient to extract
    
    Returns:
        float: Extracted value or None if not found
    """
    try:
        # Look for different patterns in the JSON string
        patterns = [
            # Pattern 1: "name": "Nutrient", "value": "123"
            f'"name"\\s*:\\s*"{nutrient_name}"\\s*,\\s*"value"\\s*:\\s*"([^"]*)"',
            # Pattern 2: "name":"Nutrient","value":123
            f'"name"\\s*:\\s*"{nutrient_name}"\\s*,\\s*"value"\\s*:\\s*([0-9\\.]+)',
            # Pattern 3: name as key: "Nutrient": 123
            f'"{nutrient_name}"\\s*:\\s*([0-9\\.]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, json_str, re.IGNORECASE)
            if matches:
                value = matches[0]
                # Try to convert to float
                try:
                    return float(value)
                except ValueError:
                    # If conversion fails, try to clean the string
                    cleaned = re.sub(r'[^\d\.]', '', value)
                    return float(cleaned) if cleaned else None
        
        return None
    except Exception:
        return None 