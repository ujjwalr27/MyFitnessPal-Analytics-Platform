from sqlalchemy import create_engine, Column, Integer, Float, Date, String, MetaData, Table, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask import current_app
import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Base = declarative_base()

class FitnessData(Base):
  
    __tablename__ = 'fitness_data'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    calories = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    protein = Column(Float)
    sodium = Column(Float)
    sugar = Column(Float)
    exercise_calories = Column(Float)
    steps = Column(Integer)
    carbs_calories = Column(Float)
    fat_calories = Column(Float)
    protein_calories = Column(Float)
    net_calories = Column(Float)
    created_at = Column(Date, default=datetime.utcnow)

def get_engine():
   
    return create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])

def get_session():
 
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def init_db():
    
    try:
        engine = get_engine()
        inspector = inspect(engine)
        
       
        if 'fitness_data' in inspector.get_table_names():
            columns = [column['name'] for column in inspector.get_columns('fitness_data')]
            
         
            if 'user_id' not in columns:
                logger.warning("Existing table doesn't have user_id column. Recreating table...")
                
                metadata = MetaData()
                metadata.reflect(bind=engine)
                if 'fitness_data' in metadata.tables:
                    fitness_table = metadata.tables['fitness_data']
                    fitness_table.drop(engine)
                    logger.info("Dropped existing fitness_data table.")
        
        
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def insert_fitness_data(df):
   
    try:
       
        if df['date'].dtype != 'datetime64[ns]':
            df['date'] = pd.to_datetime(df['date']).dt.date
        else:
            df['date'] = df['date'].dt.date
        
        
        session = get_session()
        
        records_inserted = 0
        
        try:
            for _, row in df.iterrows():
                existing = session.query(FitnessData).filter_by(
                    user_id=row['user_id'],
                    date=row['date']
                ).first()
                
                if existing:
                    for column, value in row.items():
                        if column not in ['user_id', 'date'] and hasattr(existing, column):
                            setattr(existing, column, value)
                else:
                    data_dict = row.to_dict()
                    new_record = FitnessData(**data_dict)
                    session.add(new_record)
                
                records_inserted += 1
            
            session.commit()
            logger.info(f"Successfully inserted/updated {records_inserted} records.")
            return records_inserted
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error inserting data into PostgreSQL: {str(e)}")
        raise ValueError(f"Database error: {str(e)}") 