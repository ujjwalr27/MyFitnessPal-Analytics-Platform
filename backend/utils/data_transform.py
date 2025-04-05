import pandas as pd
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def transform_data(df):
    """
    Transform parsed MyFitnessPal data into a format suitable for database storage.
    
    Args:
        df (pd.DataFrame): Parsed dataframe from CSV
        
    Returns:
        pd.DataFrame: Transformed dataframe ready for database insertion
    """
    # Create a copy to avoid modifying the original
    transformed_df = df.copy()
    
    # Handle NaN values
    transformed_df = transformed_df.replace({np.nan: None})
    
    # Calculate derived values - only if we have the necessary data
    # Calculate macronutrient calories if macronutrient data is available
    columns_to_check = ['carbs', 'fat', 'protein']
    if all(col in transformed_df.columns for col in columns_to_check):
        # Fill missing values with 0 for calculation purposes
        calc_df = transformed_df[columns_to_check].fillna(0)
        
        transformed_df['carbs_calories'] = calc_df['carbs'] * 4  # 4 calories per gram of carbs
        transformed_df['fat_calories'] = calc_df['fat'] * 9      # 9 calories per gram of fat
        transformed_df['protein_calories'] = calc_df['protein'] * 4  # 4 calories per gram of protein
    
    # Calculate net calories if both calories and exercise_calories are available
    if 'calories' in transformed_df.columns and 'exercise_calories' in transformed_df.columns:
        # First, check if exercise_calories exists in the dataframe
        if 'exercise_calories' not in transformed_df.columns:
            transformed_df['exercise_calories'] = 0
        
        # Fill missing values with 0 for calculation
        calc_df = transformed_df[['calories', 'exercise_calories']].fillna(0)
        transformed_df['net_calories'] = calc_df['calories'] - calc_df['exercise_calories']
    
    logger.info(f"Data transformed successfully with {len(transformed_df)} records and {len(transformed_df.columns)} fields.")
    
    return transformed_df 