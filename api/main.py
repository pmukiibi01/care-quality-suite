from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List, Optional
import os
import pandas as pd
from datetime import datetime, date
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/value_based_care")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(
    title="Value-Based Care Quality Suite",
    description="API for HEDIS/HVBP quality measures automation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QualityMeasure(BaseModel):
    measure_id: str
    measure_name: str
    denominator: int
    numerator: int
    rate: float
    measurement_date: date

class PatientMeasure(BaseModel):
    patient_id: str
    mrn: str
    full_name: str
    age_years: int
    denominator: int
    numerator: int
    measurement_date: date

class MeasureSummary(BaseModel):
    measure_id: str
    measure_name: str
    total_denominator: int
    total_numerator: int
    overall_rate: float
    patient_details: List[PatientMeasure]

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Value-Based Care Quality Suite API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed")

@app.get("/measures", response_model=List[QualityMeasure])
async def get_quality_measures():
    """Get all available quality measures with summary statistics"""
    measures = []
    
    # HEDIS Diabetes Care - Hemoglobin A1c
    try:
        query = """
        SELECT 
            'HEDIS-DM-A1C' as measure_id,
            'Diabetes Care - Hemoglobin A1c' as measure_name,
            SUM(denominator) as denominator,
            SUM(numerator) as numerator,
            CASE 
                WHEN SUM(denominator) > 0 
                THEN ROUND((SUM(numerator)::float / SUM(denominator)) * 100, 2)
                ELSE 0 
            END as rate,
            CURRENT_DATE as measurement_date
        FROM quality_measures.hedis_diabetes_care_hemoglobin_a1c
        """
        with engine.connect() as connection:
            result = connection.execute(text(query))
            row = result.fetchone()
            if row:
                measures.append(QualityMeasure(
                    measure_id=row[0],
                    measure_name=row[1],
                    denominator=row[2] or 0,
                    numerator=row[3] or 0,
                    rate=row[4] or 0.0,
                    measurement_date=row[5]
                ))
    except Exception as e:
        logger.error(f"Error getting diabetes A1c measure: {e}")
    
    # HEDIS Breast Cancer Screening
    try:
        query = """
        SELECT 
            'HEDIS-BCS' as measure_id,
            'Breast Cancer Screening' as measure_name,
            SUM(denominator) as denominator,
            SUM(numerator) as numerator,
            CASE 
                WHEN SUM(denominator) > 0 
                THEN ROUND((SUM(numerator)::float / SUM(denominator)) * 100, 2)
                ELSE 0 
            END as rate,
            CURRENT_DATE as measurement_date
        FROM quality_measures.hedis_breast_cancer_screening
        """
        with engine.connect() as connection:
            result = connection.execute(text(query))
            row = result.fetchone()
            if row:
                measures.append(QualityMeasure(
                    measure_id=row[0],
                    measure_name=row[1],
                    denominator=row[2] or 0,
                    numerator=row[3] or 0,
                    rate=row[4] or 0.0,
                    measurement_date=row[5]
                ))
    except Exception as e:
        logger.error(f"Error getting breast cancer screening measure: {e}")
    
    # HVBP Patient Safety Indicator
    try:
        query = """
        SELECT 
            'HVBP-PSI-04' as measure_id,
            'Death among surgical inpatients' as measure_name,
            SUM(denominator) as denominator,
            SUM(numerator) as numerator,
            CASE 
                WHEN SUM(denominator) > 0 
                THEN ROUND((SUM(numerator)::float / SUM(denominator)) * 100, 2)
                ELSE 0 
            END as rate,
            CURRENT_DATE as measurement_date
        FROM quality_measures.hvbp_patient_safety_indicator
        """
        with engine.connect() as connection:
            result = connection.execute(text(query))
            row = result.fetchone()
            if row:
                measures.append(QualityMeasure(
                    measure_id=row[0],
                    measure_name=row[1],
                    denominator=row[2] or 0,
                    numerator=row[3] or 0,
                    rate=row[4] or 0.0,
                    measurement_date=row[5]
                ))
    except Exception as e:
        logger.error(f"Error getting PSI measure: {e}")
    
    return measures

@app.get("/measures/{measure_id}", response_model=MeasureSummary)
async def get_measure_details(measure_id: str):
    """Get detailed information for a specific quality measure"""
    
    if measure_id == "HEDIS-DM-A1C":
        table_name = "quality_measures.hedis_diabetes_care_hemoglobin_a1c"
        measure_name = "Diabetes Care - Hemoglobin A1c"
    elif measure_id == "HEDIS-BCS":
        table_name = "quality_measures.hedis_breast_cancer_screening"
        measure_name = "Breast Cancer Screening"
    elif measure_id == "HVBP-PSI-04":
        table_name = "quality_measures.hvbp_patient_safety_indicator"
        measure_name = "Death among surgical inpatients"
    else:
        raise HTTPException(status_code=404, detail="Measure not found")
    
    try:
        # Get summary statistics
        summary_query = f"""
        SELECT 
            SUM(denominator) as total_denominator,
            SUM(numerator) as total_numerator,
            CASE 
                WHEN SUM(denominator) > 0 
                THEN ROUND((SUM(numerator)::float / SUM(denominator)) * 100, 2)
                ELSE 0 
            END as overall_rate
        FROM {table_name}
        """
        
        # Get patient details
        details_query = f"""
        SELECT 
            patient_id,
            mrn,
            full_name,
            age_years,
            denominator,
            numerator,
            measurement_date
        FROM {table_name}
        ORDER BY full_name
        """
        
        with engine.connect() as connection:
            # Get summary
            summary_result = connection.execute(text(summary_query))
            summary_row = summary_result.fetchone()
            
            # Get patient details
            details_result = connection.execute(text(details_query))
            details_rows = details_result.fetchall()
            
            patient_details = [
                PatientMeasure(
                    patient_id=str(row[0]),
                    mrn=row[1],
                    full_name=row[2],
                    age_years=row[3],
                    denominator=row[4],
                    numerator=row[5],
                    measurement_date=row[6]
                )
                for row in details_rows
            ]
            
            return MeasureSummary(
                measure_id=measure_id,
                measure_name=measure_name,
                total_denominator=summary_row[0] or 0,
                total_numerator=summary_row[1] or 0,
                overall_rate=summary_row[2] or 0.0,
                patient_details=patient_details
            )
            
    except Exception as e:
        logger.error(f"Error getting measure details for {measure_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/measures/refresh")
async def refresh_measures():
    """Trigger refresh of all quality measures"""
    try:
        # This would typically trigger dbt run in a production environment
        # For now, we'll just return a success message
        logger.info("Quality measures refresh requested")
        return {"message": "Quality measures refresh initiated", "status": "success"}
    except Exception as e:
        logger.error(f"Error refreshing measures: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh measures")

@app.get("/patients/{patient_id}/measures")
async def get_patient_measures(patient_id: str):
    """Get all quality measures for a specific patient"""
    
    measures = []
    
    try:
        # Check diabetes A1c measure
        query = """
        SELECT 
            'HEDIS-DM-A1C' as measure_id,
            'Diabetes Care - Hemoglobin A1c' as measure_name,
            denominator,
            numerator,
            most_recent_a1c,
            most_recent_a1c_date
        FROM quality_measures.hedis_diabetes_care_hemoglobin_a1c
        WHERE patient_id = :patient_id
        """
        with engine.connect() as connection:
            result = connection.execute(text(query), {"patient_id": patient_id})
            row = result.fetchone()
            if row:
                measures.append({
                    "measure_id": row[0],
                    "measure_name": row[1],
                    "denominator": row[2],
                    "numerator": row[3],
                    "additional_info": {
                        "most_recent_a1c": row[4],
                        "most_recent_a1c_date": row[5]
                    }
                })
        
        # Check breast cancer screening
        query = """
        SELECT 
            'HEDIS-BCS' as measure_id,
            'Breast Cancer Screening' as measure_name,
            denominator,
            numerator,
            last_screening_date,
            screening_count
        FROM quality_measures.hedis_breast_cancer_screening
        WHERE patient_id = :patient_id
        """
        with engine.connect() as connection:
            result = connection.execute(text(query), {"patient_id": patient_id})
            row = result.fetchone()
            if row:
                measures.append({
                    "measure_id": row[0],
                    "measure_name": row[1],
                    "denominator": row[2],
                    "numerator": row[3],
                    "additional_info": {
                        "last_screening_date": row[4],
                        "screening_count": row[5]
                    }
                })
        
        return {"patient_id": patient_id, "measures": measures}
        
    except Exception as e:
        logger.error(f"Error getting patient measures for {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)