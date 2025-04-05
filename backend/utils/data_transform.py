import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def transform_data(df):
   
    transformed_df = df.copy()
    
    transformed_df = transformed_df.replace({np.nan: None})
    
    
    columns_to_check = ['carbs', 'fat', 'protein']
    if all(col in transformed_df.columns for col in columns_to_check):
        calc_df = transformed_df[columns_to_check].fillna(0)
        
        transformed_df['carbs_calories'] = calc_df['carbs'] * 4  
        transformed_df['fat_calories'] = calc_df['fat'] * 9     
        transformed_df['protein_calories'] = calc_df['protein'] * 4  
    if 'calories' in transformed_df.columns and 'exercise_calories' in transformed_df.columns:
        if 'exercise_calories' not in transformed_df.columns:
            transformed_df['exercise_calories'] = 0
        
        calc_df = transformed_df[['calories', 'exercise_calories']].fillna(0)
        transformed_df['net_calories'] = calc_df['calories'] - calc_df['exercise_calories']
    
    logger.info(f"Data transformed successfully with {len(transformed_df)} records and {len(transformed_df.columns)} fields.")
    
    return transformed_df 