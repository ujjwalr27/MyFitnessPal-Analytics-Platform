import pandas as pd
import numpy as np
import logging
import json
import re

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_csv(file_path):
   
    try:
       
        df = pd.read_csv(file_path)
        
        if df.empty:
            raise ValueError("The uploaded CSV file is empty.")
        
        
        if len(df.columns) < 3:
            raise ValueError("CSV does not have enough columns. Expected at least 3 columns.")
        
       
        column_mapping = {}
        for i, col in enumerate(df.columns):
            if i == 0:
                column_mapping[col] = 'user_id'
            elif i == 1:
                column_mapping[col] = 'date'
            else:
                column_mapping[col] = f'data_{i-1}'
        
        df = df.rename(columns=column_mapping)
        
        
        try:
           
            date_sample = df['date'].iloc[0] if not df.empty else ""
            
            if re.match(r'^\d{2}-\d{2}-\d{4}$', str(date_sample)):
              
                date_format = '%d-%m-%Y'
            elif re.match(r'^\d{4}-\d{2}-\d{2}$', str(date_sample)):
                
                date_format = '%Y-%m-%d'
            else:
               
                date_format = None
                
            if date_format:
                df['date'] = pd.to_datetime(df['date'], format=date_format)
            else:
                df['date'] = pd.to_datetime(df['date'])
                
        except Exception as e:
            logger.warning(f"Date format conversion warning: {str(e)}")
           
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            if df['date'].isna().any():
                raise ValueError("Could not parse date column. Please check the date format.")
        
       
        processed_data = []
        
        for _, row in df.iterrows():
            user_id = row['user_id']
            date = row['date']
            
           
            json_data = ""
            for col in df.columns:
                if col.startswith('data_'):
                    if pd.notna(row[col]):
                        json_data += str(row[col])
            
            
            try:
               
                json_data = json_data.replace("'", '"')
                
                nutrition_data = extract_nutrition_data(json_data, user_id, date)
                processed_data.extend(nutrition_data)
                
            except Exception as e:
                logger.warning(f"Error processing JSON for user {user_id} on {date}: {str(e)}")
               
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
        
       
        record['calories'] = extract_value(json_str, 'Calories')
        record['carbs'] = extract_value(json_str, 'Carbs')
        record['fat'] = extract_value(json_str, 'Fat')
        record['protein'] = extract_value(json_str, 'Protein')
        record['sodium'] = extract_value(json_str, 'Sodium')
        record['sugar'] = extract_value(json_str, 'Sugar')
        
        if record['calories'] is None and record['carbs'] is None:
            try:
                json_data = json.loads(json_str)
                
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
                pass
        
        data.append(record)
        return data
        
    except Exception as e:
        logger.error(f"Error extracting nutrition data: {str(e)}")
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
  
    try:
        patterns = [
            f'"name"\\s*:\\s*"{nutrient_name}"\\s*,\\s*"value"\\s*:\\s*"([^"]*)"',
            f'"name"\\s*:\\s*"{nutrient_name}"\\s*,\\s*"value"\\s*:\\s*([0-9\\.]+)',
            f'"{nutrient_name}"\\s*:\\s*([0-9\\.]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, json_str, re.IGNORECASE)
            if matches:
                value = matches[0]
                try:
                    return float(value)
                except ValueError:
                    cleaned = re.sub(r'[^\d\.]', '', value)
                    return float(cleaned) if cleaned else None
        
        return None
    except Exception:
        return None 