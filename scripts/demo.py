#!/usr/bin/env python3
"""
Demo script to showcase the Value-Based Care Quality Suite project structure and features.
"""

import os
import json
from pathlib import Path

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")

def print_subsection(title):
    """Print a formatted subsection header."""
    print(f"\n🔹 {title}")
    print("-" * 40)

def show_project_structure():
    """Display the project directory structure."""
    print_section("PROJECT STRUCTURE")
    
    def print_tree(directory, prefix="", max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return
            
        items = sorted(Path(directory).iterdir())
        for i, item in enumerate(items):
            if item.name.startswith('.'):
                continue
                
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir() and current_depth < max_depth - 1:
                next_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(item, next_prefix, max_depth, current_depth + 1)
    
    print_tree(".")

def show_quality_measures():
    """Display information about implemented quality measures."""
    print_section("QUALITY MEASURES")
    
    measures = {
        "HEDIS Measures": [
            {
                "id": "HEDIS-DM-A1C",
                "name": "Diabetes Care - Hemoglobin A1c",
                "description": "Members 18-75 with diabetes and HbA1c < 8.0%",
                "file": "dbt/models/quality_measures/hedis_diabetes_care_hemoglobin_a1c.sql"
            },
            {
                "id": "HEDIS-BCS", 
                "name": "Breast Cancer Screening",
                "description": "Women 50-74 with mammography within past 2 years",
                "file": "dbt/models/quality_measures/hedis_breast_cancer_screening.sql"
            }
        ],
        "HVBP Measures": [
            {
                "id": "HVBP-PSI-04",
                "name": "Death among surgical inpatients",
                "description": "PSI-04: Surgical inpatient mortality rate",
                "file": "dbt/models/quality_measures/hvbp_patient_safety_indicator.sql"
            }
        ]
    }
    
    for category, measure_list in measures.items():
        print_subsection(category)
        for measure in measure_list:
            print(f"  📊 {measure['id']}: {measure['name']}")
            print(f"     {measure['description']}")
            print(f"     📁 {measure['file']}")

def show_api_endpoints():
    """Display API endpoint information."""
    print_section("API ENDPOINTS")
    
    endpoints = [
        {
            "method": "GET",
            "path": "/",
            "description": "Root endpoint with API information"
        },
        {
            "method": "GET", 
            "path": "/health",
            "description": "Health check endpoint"
        },
        {
            "method": "GET",
            "path": "/measures",
            "description": "Get all quality measures with summary statistics"
        },
        {
            "method": "GET",
            "path": "/measures/{measure_id}",
            "description": "Get detailed information for a specific measure"
        },
        {
            "method": "POST",
            "path": "/measures/refresh",
            "description": "Trigger refresh of all quality measures"
        },
        {
            "method": "GET",
            "path": "/patients/{patient_id}/measures",
            "description": "Get all quality measures for a specific patient"
        }
    ]
    
    for endpoint in endpoints:
        print(f"  🔗 {endpoint['method']} {endpoint['path']}")
        print(f"     {endpoint['description']}")

def show_sample_data():
    """Display information about sample data."""
    print_section("SAMPLE DATA")
    
    data_files = [
        {
            "file": "patients.csv",
            "description": "Patient demographics and basic information",
            "rows": "10 patients with demographics"
        },
        {
            "file": "encounters.csv", 
            "description": "Healthcare encounters (inpatient, outpatient, emergency)",
            "rows": "10 encounters across different types"
        },
        {
            "file": "diagnoses.csv",
            "description": "ICD-10 diagnosis codes and types",
            "rows": "13 diagnosis records"
        },
        {
            "file": "lab_results.csv",
            "description": "Laboratory test results including A1C values",
            "rows": "9 lab results"
        },
        {
            "file": "procedures.csv",
            "description": "CPT procedure codes including mammography",
            "rows": "9 procedure records"
        }
    ]
    
    for data_file in data_files:
        print(f"  📄 {data_file['file']}")
        print(f"     {data_file['description']}")
        print(f"     📊 {data_file['rows']}")

def show_tech_stack():
    """Display the technology stack."""
    print_section("TECHNOLOGY STACK")
    
    stack = {
        "Data Processing": ["dbt (data build tool)", "PostgreSQL", "SQL"],
        "API & Web": ["FastAPI", "SQLAlchemy", "Uvicorn"],
        "Data Quality": ["Great Expectations", "pytest"],
        "Containerization": ["Docker", "Docker Compose"],
        "CI/CD": ["GitHub Actions"],
        "Testing": ["pytest", "FastAPI TestClient"]
    }
    
    for category, technologies in stack.items():
        print_subsection(category)
        for tech in technologies:
            print(f"  🔧 {tech}")

def show_deployment_info():
    """Display deployment and usage information."""
    print_section("DEPLOYMENT & USAGE")
    
    print_subsection("Quick Start Commands")
    commands = [
        "docker-compose up -d",
        "python scripts/load_sample_data.py",
        "docker-compose exec dbt dbt run",
        "curl http://localhost:8000/health"
    ]
    
    for cmd in commands:
        print(f"  💻 {cmd}")
    
    print_subsection("API Documentation")
    print("  📚 http://localhost:8000/docs - Interactive API documentation")
    print("  📊 http://localhost:8000/measures - Quality measures endpoint")
    
    print_subsection("Testing")
    test_commands = [
        "python -m pytest tests/ -v",
        "python -m pytest tests/test_api.py -v",
        "python -m pytest tests/test_data_quality.py -v"
    ]
    
    for cmd in test_commands:
        print(f"  🧪 {cmd}")

def main():
    """Run the demo."""
    print("🚀 VALUE-BASED CARE QUALITY SUITE")
    print("🏥 HEDIS/HVBP Quality Measures Automation Platform")
    print("📅 2025 Implementation")
    
    show_project_structure()
    show_quality_measures()
    show_api_endpoints()
    show_sample_data()
    show_tech_stack()
    show_deployment_info()
    
    print_section("PROJECT SUMMARY")
    print("✅ Complete HEDIS/HVBP quality measures automation system")
    print("✅ Docker-based deployment with PostgreSQL database")
    print("✅ FastAPI web service with comprehensive API endpoints")
    print("✅ dbt models for data transformation and measure calculation")
    print("✅ Great Expectations for data quality validation")
    print("✅ Comprehensive test suite with pytest")
    print("✅ GitHub Actions CI/CD pipeline")
    print("✅ Sample data and documentation")
    
    print(f"\n🎉 Project successfully implemented and ready for deployment!")
    print(f"📁 Location: {os.getcwd()}")

if __name__ == "__main__":
    main()