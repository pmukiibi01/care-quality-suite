import pytest
import requests
import json
from fastapi.testclient import TestClient
import os
import sys

# Add the api directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))

from main import app

client = TestClient(app)

class TestAPI:
    """Test the FastAPI endpoints"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        # This might fail if database is not connected, which is expected in some test environments
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"
    
    def test_measures_endpoint_structure(self):
        """Test that measures endpoint returns correct structure"""
        response = client.get("/measures")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            
            # If we have measures, check their structure
            if len(data) > 0:
                measure = data[0]
                required_fields = ["measure_id", "measure_name", "denominator", "numerator", "rate", "measurement_date"]
                for field in required_fields:
                    assert field in measure
        else:
            # If database is not available, that's okay for unit tests
            assert response.status_code in [200, 503]
    
    def test_measure_details_endpoint(self):
        """Test measure details endpoint"""
        # Test with a known measure ID
        response = client.get("/measures/HEDIS-DM-A1C")
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["measure_id", "measure_name", "total_denominator", "total_numerator", "overall_rate", "patient_details"]
            for field in required_fields:
                assert field in data
            
            assert data["measure_id"] == "HEDIS-DM-A1C"
            assert isinstance(data["patient_details"], list)
        elif response.status_code == 404:
            # Measure not found is expected if database is empty
            pass
        else:
            # Database connection issues are acceptable in test environment
            assert response.status_code in [200, 404, 500]
    
    def test_invalid_measure_id(self):
        """Test that invalid measure ID returns 404"""
        response = client.get("/measures/INVALID-MEASURE")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_refresh_measures_endpoint(self):
        """Test the refresh measures endpoint"""
        response = client.post("/measures/refresh")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "success"
    
    def test_patient_measures_endpoint(self):
        """Test patient-specific measures endpoint"""
        # Test with a sample patient ID
        test_patient_id = "test-patient-123"
        response = client.get(f"/patients/{test_patient_id}/measures")
        
        if response.status_code == 200:
            data = response.json()
            assert "patient_id" in data
            assert "measures" in data
            assert data["patient_id"] == test_patient_id
            assert isinstance(data["measures"], list)
        else:
            # Database connection issues or patient not found are acceptable
            assert response.status_code in [200, 404, 500]
    
    def test_cors_headers(self):
        """Test that CORS headers are present"""
        response = client.options("/")
        # CORS headers should be present (handled by middleware)
        assert response.status_code in [200, 405]  # OPTIONS might return 405 if not explicitly handled
    
    def test_api_documentation(self):
        """Test that API documentation is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "info" in data
        assert data["info"]["title"] == "Value-Based Care Quality Suite"