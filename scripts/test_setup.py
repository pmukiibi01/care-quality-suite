#!/usr/bin/env python3
"""
Test script to validate the project setup without Docker.
This script checks file structure, syntax, and basic functionality.
"""

import os
import sys
import ast
import importlib.util
from pathlib import Path

def check_file_structure():
    """Check that all required files and directories exist."""
    required_files = [
        "Dockerfile",
        "docker-compose.yml",
        "requirements.txt",
        "README.md",
        ".gitignore",
        "api/main.py",
        "dbt/dbt_project.yml",
        "dbt/profiles.yml",
        "dbt/models/staging/stg_patients.sql",
        "dbt/models/marts/dim_patients.sql",
        "dbt/models/quality_measures/hedis_diabetes_care_hemoglobin_a1c.sql",
        "tests/test_api.py",
        "tests/test_data_quality.py",
        "data/sample_data/patients.csv",
        ".github/workflows/ci.yml"
    ]
    
    required_dirs = [
        "api",
        "dbt/models/staging",
        "dbt/models/marts", 
        "dbt/models/quality_measures",
        "tests",
        "data/sample_data",
        "scripts",
        ".github/workflows"
    ]
    
    print("🔍 Checking file structure...")
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    print("✅ All required files and directories exist")
    return True

def check_python_syntax():
    """Check Python syntax for all Python files."""
    print("\n🔍 Checking Python syntax...")
    
    python_files = [
        "api/main.py",
        "tests/test_api.py", 
        "tests/test_data_quality.py",
        "scripts/load_sample_data.py"
    ]
    
    syntax_errors = []
    
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    source = f.read()
                ast.parse(source)
                print(f"✅ {file_path} - syntax OK")
            except SyntaxError as e:
                syntax_errors.append(f"{file_path}: {e}")
                print(f"❌ {file_path} - syntax error: {e}")
    
    if syntax_errors:
        print(f"\n❌ Syntax errors found: {syntax_errors}")
        return False
    
    print("✅ All Python files have valid syntax")
    return True

def check_sql_syntax():
    """Basic check of SQL files."""
    print("\n🔍 Checking SQL files...")
    
    sql_files = [
        "dbt/models/staging/stg_patients.sql",
        "dbt/models/marts/dim_patients.sql",
        "dbt/models/quality_measures/hedis_diabetes_care_hemoglobin_a1c.sql"
    ]
    
    all_valid = True
    for file_path in sql_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                # Basic check - file should not be empty and should contain SQL keywords
                if content.strip() and any(keyword in content.upper() for keyword in ['SELECT', 'FROM', 'WHERE']):
                    print(f"✅ {file_path} - looks like valid SQL")
                else:
                    print(f"⚠️  {file_path} - might not contain valid SQL")
                    all_valid = False
            except Exception as e:
                print(f"❌ {file_path} - error reading file: {e}")
                all_valid = False
    
    return all_valid

def check_yaml_syntax():
    """Check YAML files."""
    print("\n🔍 Checking YAML files...")
    
    yaml_files = [
        "dbt/dbt_project.yml",
        "dbt/profiles.yml",
        "docker-compose.yml",
        ".github/workflows/ci.yml"
    ]
    
    all_valid = True
    for file_path in yaml_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                # Basic check - should not be empty
                if content.strip():
                    print(f"✅ {file_path} - looks like valid YAML")
                else:
                    print(f"⚠️  {file_path} - appears to be empty")
                    all_valid = False
            except Exception as e:
                print(f"❌ {file_path} - error reading file: {e}")
                all_valid = False
    
    return all_valid

def check_csv_files():
    """Check CSV sample data files."""
    print("\n🔍 Checking CSV sample data...")
    
    csv_files = [
        "data/sample_data/patients.csv",
        "data/sample_data/encounters.csv", 
        "data/sample_data/diagnoses.csv",
        "data/sample_data/lab_results.csv",
        "data/sample_data/procedures.csv"
    ]
    
    all_valid = True
    for file_path in csv_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                if len(lines) > 1:  # Should have header + at least one data row
                    print(f"✅ {file_path} - has {len(lines)-1} data rows")
                else:
                    print(f"⚠️  {file_path} - appears to have no data rows")
                    all_valid = False
            except Exception as e:
                print(f"❌ {file_path} - error reading file: {e}")
                all_valid = False
    
    return all_valid

def check_requirements():
    """Check requirements.txt file."""
    print("\n🔍 Checking requirements.txt...")
    
    if os.path.exists("requirements.txt"):
        try:
            with open("requirements.txt", 'r') as f:
                content = f.read()
            
            # Check for key dependencies
            required_packages = [
                "fastapi",
                "uvicorn", 
                "sqlalchemy",
                "psycopg2-binary",
                "pandas",
                "great-expectations",
                "pytest"
            ]
            
            missing_packages = []
            for package in required_packages:
                if package not in content:
                    missing_packages.append(package)
            
            if missing_packages:
                print(f"⚠️  Missing packages in requirements.txt: {missing_packages}")
                return False
            else:
                print("✅ All required packages found in requirements.txt")
                return True
                
        except Exception as e:
            print(f"❌ Error reading requirements.txt: {e}")
            return False
    else:
        print("❌ requirements.txt not found")
        return False

def main():
    """Run all checks."""
    print("🚀 Value-Based Care Quality Suite - Setup Validation")
    print("=" * 60)
    
    checks = [
        check_file_structure,
        check_python_syntax,
        check_sql_syntax,
        check_yaml_syntax,
        check_csv_files,
        check_requirements
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Error running {check.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    
    passed = sum(1 for r in results if r is not False)
    total = len([r for r in results if r is not None])
    
    if passed == total:
        print("🎉 All checks passed! The project is ready for deployment.")
        print("\n📋 Next steps:")
        print("1. Run: docker-compose up -d")
        print("2. Load sample data: python scripts/load_sample_data.py")
        print("3. Run dbt models: docker-compose exec dbt dbt run")
        print("4. Test API: curl http://localhost:8000/health")
        return 0
    else:
        print(f"⚠️  {passed}/{total} checks passed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())