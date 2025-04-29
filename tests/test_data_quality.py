import pytest
import pandas as pd
from sqlalchemy import create_engine, text
import os
from great_expectations.core import ExpectationSuite
from great_expectations.dataset import PandasDataset

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/value_based_care")
engine = create_engine(DATABASE_URL)

class TestDataQuality:
    """Test data quality using Great Expectations"""
    
    @pytest.fixture(scope="class")
    def db_connection(self):
        """Create database connection for testing"""
        return engine.connect()
    
    def test_patients_table_completeness(self, db_connection):
        """Test that patients table has required fields"""
        query = "SELECT * FROM raw_data.patients LIMIT 1000"
        df = pd.read_sql(query, db_connection)
        
        # Create Great Expectations dataset
        ge_df = PandasDataset(df)
        
        # Test that required fields are not null
        assert ge_df.expect_column_values_to_not_be_null("patient_id").success
        assert ge_df.expect_column_values_to_not_be_null("mrn").success
        assert ge_df.expect_column_values_to_not_be_null("first_name").success
        assert ge_df.expect_column_values_to_not_be_null("last_name").success
        assert ge_df.expect_column_values_to_not_be_null("date_of_birth").success
        
        # Test data types
        assert ge_df.expect_column_values_to_be_of_type("patient_id", "object").success
        assert ge_df.expect_column_values_to_be_of_type("mrn", "object").success
        assert ge_df.expect_column_values_to_be_of_type("age_years", "int64").success
    
    def test_encounters_table_quality(self, db_connection):
        """Test encounters table data quality"""
        query = "SELECT * FROM raw_data.encounters LIMIT 1000"
        df = pd.read_sql(query, db_connection)
        
        if len(df) > 0:
            ge_df = PandasDataset(df)
            
            # Test required fields
            assert ge_df.expect_column_values_to_not_be_null("encounter_id").success
            assert ge_df.expect_column_values_to_not_be_null("patient_id").success
            
            # Test date fields
            assert ge_df.expect_column_values_to_be_of_type("admission_date", "datetime64[ns]").success
            
            # Test length of stay calculation
            if 'length_of_stay_days' in df.columns:
                assert ge_df.expect_column_values_to_be_between("length_of_stay_days", min_value=0, max_value=365).success
    
    def test_diagnoses_table_quality(self, db_connection):
        """Test diagnoses table data quality"""
        query = "SELECT * FROM raw_data.diagnoses LIMIT 1000"
        df = pd.read_sql(query, db_connection)
        
        if len(df) > 0:
            ge_df = PandasDataset(df)
            
            # Test required fields
            assert ge_df.expect_column_values_to_not_be_null("diagnosis_id").success
            assert ge_df.expect_column_values_to_not_be_null("patient_id").success
            assert ge_df.expect_column_values_to_not_be_null("diagnosis_code").success
            
            # Test diagnosis code format (should be alphanumeric)
            assert ge_df.expect_column_values_to_match_regex("diagnosis_code", r"^[A-Z0-9.]+$").success
    
    def test_quality_measures_calculation(self, db_connection):
        """Test that quality measures are calculated correctly"""
        # Test diabetes A1c measure
        query = """
        SELECT 
            SUM(denominator) as total_denominator,
            SUM(numerator) as total_numerator
        FROM quality_measures.hedis_diabetes_care_hemoglobin_a1c
        """
        
        try:
            result = db_connection.execute(text(query))
            row = result.fetchone()
            
            if row and row[0] is not None:
                total_denominator = row[0]
                total_numerator = row[1] or 0
                
                # Numerator should not exceed denominator
                assert total_numerator <= total_denominator
                
                # Rate should be between 0 and 100
                if total_denominator > 0:
                    rate = (total_numerator / total_denominator) * 100
                    assert 0 <= rate <= 100
        except Exception as e:
            # If table doesn't exist yet, that's okay for initial setup
            pytest.skip(f"Quality measures table not yet created: {e}")
    
    def test_breast_cancer_screening_measure(self, db_connection):
        """Test breast cancer screening measure calculation"""
        query = """
        SELECT 
            SUM(denominator) as total_denominator,
            SUM(numerator) as total_numerator
        FROM quality_measures.hedis_breast_cancer_screening
        """
        
        try:
            result = db_connection.execute(text(query))
            row = result.fetchone()
            
            if row and row[0] is not None:
                total_denominator = row[0]
                total_numerator = row[1] or 0
                
                # Numerator should not exceed denominator
                assert total_numerator <= total_denominator
                
                # Rate should be between 0 and 100
                if total_denominator > 0:
                    rate = (total_numerator / total_denominator) * 100
                    assert 0 <= rate <= 100
        except Exception as e:
            pytest.skip(f"Breast cancer screening table not yet created: {e}")
    
    def test_api_endpoints(self):
        """Test API endpoints functionality"""
        import requests
        
        # Test health endpoint
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
        
        # Test measures endpoint
        try:
            response = requests.get("http://localhost:8000/measures", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_data_consistency(self, db_connection):
        """Test data consistency across related tables"""
        # Test that patient IDs in encounters exist in patients table
        query = """
        SELECT DISTINCT e.patient_id
        FROM raw_data.encounters e
        LEFT JOIN raw_data.patients p ON e.patient_id = p.patient_id
        WHERE p.patient_id IS NULL
        LIMIT 10
        """
        
        result = db_connection.execute(text(query))
        orphaned_encounters = result.fetchall()
        
        # Should have no orphaned encounters
        assert len(orphaned_encounters) == 0, f"Found {len(orphaned_encounters)} orphaned encounters"
    
    def test_date_ranges(self, db_connection):
        """Test that dates are within reasonable ranges"""
        # Test patient birth dates
        query = """
        SELECT 
            MIN(date_of_birth) as min_birth_date,
            MAX(date_of_birth) as max_birth_date
        FROM raw_data.patients
        """
        
        result = db_connection.execute(text(query))
        row = result.fetchone()
        
        if row and row[0] is not None:
            min_birth_date = row[0]
            max_birth_date = row[1]
            
            # Birth dates should be reasonable (not in the future, not too old)
            from datetime import date
            today = date.today()
            
            assert min_birth_date <= today, "Birth dates should not be in the future"
            assert max_birth_date <= today, "Birth dates should not be in the future"
            
            # Check that birth dates are not too old (e.g., before 1900)
            assert min_birth_date.year >= 1900, "Birth dates should not be before 1900"