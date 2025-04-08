#!/usr/bin/env python3
"""
Script to load sample data into the database for testing and development.
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_sample_data():
    """Load sample data from CSV files into the database."""
    
    # Database configuration
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/value_based_care")
    
    try:
        # Create database connection
        engine = create_engine(database_url)
        
        # Data directory
        data_dir = "data/sample_data"
        
        # Tables and their corresponding CSV files
        tables = [
            ("raw_data.patients", "patients.csv"),
            ("raw_data.encounters", "encounters.csv"),
            ("raw_data.diagnoses", "diagnoses.csv"),
            ("raw_data.lab_results", "lab_results.csv"),
            ("raw_data.procedures", "procedures.csv")
        ]
        
        with engine.connect() as connection:
            for table_name, csv_file in tables:
                csv_path = os.path.join(data_dir, csv_file)
                
                if os.path.exists(csv_path):
                    logger.info(f"Loading {csv_file} into {table_name}")
                    
                    # Read CSV file
                    df = pd.read_csv(csv_path)
                    
                    # Clear existing data
                    connection.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
                    
                    # Insert data
                    df.to_sql(
                        table_name.split('.')[1],  # Get table name without schema
                        engine,
                        schema=table_name.split('.')[0],  # Get schema name
                        if_exists='append',
                        index=False,
                        method='multi'
                    )
                    
                    logger.info(f"Successfully loaded {len(df)} rows into {table_name}")
                else:
                    logger.warning(f"CSV file not found: {csv_path}")
        
        logger.info("Sample data loading completed successfully!")
        
    except Exception as e:
        logger.error(f"Error loading sample data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    load_sample_data()