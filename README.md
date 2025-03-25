# Value-Based Care Quality Suite

A comprehensive platform for automating HEDIS/HVBP quality measures for provider groups. This system processes Epic Clarity/Caboodle extracts, claims data (837/835), and payer rosters to generate quality measure reports with audit-ready traceability.

## Features

- **Automated Quality Measures**: HEDIS and HVBP measure calculations
- **Data Integration**: Epic Clarity/Caboodle, claims, and payer roster processing
- **Audit Trail**: Versioned measure logic with automated lineage
- **API Access**: RESTful API for measure reporting and data access
- **Data Quality**: Great Expectations integration for data validation
- **Web Interface**: FastAPI-based web service accessible from browser

## Architecture

### Technology Stack
- **Data Processing**: dbt (data build tool)
- **Database**: PostgreSQL (with Snowflake/BigQuery support)
- **API**: FastAPI with SQLAlchemy
- **Data Quality**: Great Expectations
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest

### Data Models

#### Raw Data Schema
- `patients`: Patient demographics and basic information
- `encounters`: Healthcare encounters (inpatient, outpatient, emergency)
- `diagnoses`: ICD-10 diagnosis codes and types
- `procedures`: CPT procedure codes and dates
- `medications`: Medication prescriptions and dosages
- `lab_results`: Laboratory test results and values
- `claims`: Healthcare claims data (837/835)
- `claim_line_items`: Detailed claim line items
- `payer_rosters`: Payer enrollment and eligibility data

#### Quality Measures
- **HEDIS Measures**:
  - Diabetes Care - Hemoglobin A1c (HEDIS-DM-A1C)
  - Breast Cancer Screening (HEDIS-BCS)
  - Colorectal Cancer Screening (planned)
  - Cervical Cancer Screening (planned)
  - Childhood Immunization Status (planned)

- **HVBP Measures**:
  - Patient Safety Indicator - PSI-04 (HVBP-PSI-04)
  - Clinical Process of Care (planned)
  - Patient Experience (planned)
  - Efficiency Measures (planned)

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd value-based-care-quality
   ```

2. **Start the services**
   ```bash
   docker-compose up -d
   ```

3. **Load sample data**
   ```bash
   # Copy sample data to database
   docker-compose exec postgres psql -U postgres -d value_based_care -c "
   COPY raw_data.patients FROM '/app/data/sample_data/patients.csv' WITH CSV HEADER;
   COPY raw_data.encounters FROM '/app/data/sample_data/encounters.csv' WITH CSV HEADER;
   COPY raw_data.diagnoses FROM '/app/data/sample_data/diagnoses.csv' WITH CSV HEADER;
   COPY raw_data.lab_results FROM '/app/data/sample_data/lab_results.csv' WITH CSV HEADER;
   COPY raw_data.procedures FROM '/app/data/sample_data/procedures.csv' WITH CSV HEADER;
   "
   ```

4. **Run dbt models**
   ```bash
   docker-compose exec dbt dbt run
   ```

5. **Access the application**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Usage

### Get All Quality Measures
```bash
curl http://localhost:8000/measures
```

### Get Specific Measure Details
```bash
curl http://localhost:8000/measures/HEDIS-DM-A1C
```

### Get Patient-Specific Measures
```bash
curl http://localhost:8000/patients/{patient_id}/measures
```

### Refresh Measures
```bash
curl -X POST http://localhost:8000/measures/refresh
```

## Data Input Structure

### Sample Data Download
Sample data files are provided in the `data/sample_data/` directory:

- `patients.csv`: Patient demographics
- `encounters.csv`: Healthcare encounters
- `diagnoses.csv`: Diagnosis codes
- `procedures.csv`: Procedure codes
- `lab_results.csv`: Laboratory results

### Data Format Requirements

#### Patients Table
```csv
patient_id,mrn,first_name,last_name,date_of_birth,gender,race,ethnicity
550e8400-e29b-41d4-a716-446655440000,MRN001,John,Doe,1980-05-15,Male,White,Non-Hispanic
```

#### Encounters Table
```csv
encounter_id,patient_id,encounter_type,admission_date,discharge_date,facility_id,provider_id,primary_diagnosis_code
enc001,550e8400-e29b-41d4-a716-446655440000,Outpatient,2024-01-15 09:00:00,2024-01-15 10:30:00,FAC001,PROV001,E11.9
```

#### Lab Results Table
```csv
lab_result_id,patient_id,lab_code,lab_name,result_value,result_date,reference_range
lab001,550e8400-e29b-41d4-a716-446655440000,A1C,Hemoglobin A1c,7.2,2024-01-15 10:00:00,<7.0%
```

## Development

### Running Tests
```bash
# Run all tests
docker-compose exec tests python -m pytest tests/ -v

# Run specific test file
docker-compose exec tests python -m pytest tests/test_api.py -v

# Run data quality tests
docker-compose exec tests python -m pytest tests/test_data_quality.py -v
```

### dbt Development
```bash
# Run dbt models
docker-compose exec dbt dbt run

# Run dbt tests
docker-compose exec dbt dbt test

# Generate documentation
docker-compose exec dbt dbt docs generate

# View documentation
docker-compose exec dbt dbt docs serve
```

### Adding New Quality Measures

1. **Create dbt model** in `dbt/models/quality_measures/`
2. **Add API endpoint** in `api/main.py`
3. **Write tests** in `tests/`
4. **Update documentation**

Example measure model:
```sql
-- dbt/models/quality_measures/hedis_new_measure.sql
{{ config(materialized='table') }}

with patients as (
    select * from {{ ref('dim_patients') }}
),
-- Add your measure logic here
measure_calculation as (
    select
        patient_id,
        mrn,
        full_name,
        -- Denominator logic
        case when [condition] then 1 else 0 end as denominator,
        -- Numerator logic  
        case when [condition] and [condition] then 1 else 0 end as numerator
    from patients
)

select * from measure_calculation
where denominator = 1
```

## Production Deployment

### Environment Variables
```bash
# Database configuration
DB_HOST=your-db-host
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=your-db-name
DB_SCHEMA=your-schema

# API configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Database Setup
1. Create production database
2. Update `dbt/profiles.yml` with production credentials
3. Run dbt models: `dbt run --target prod`
4. Schedule regular data refreshes

### Monitoring
- API health checks: `/health`
- Data quality monitoring with Great Expectations
- Automated testing in CI/CD pipeline

## Quality Measures Details

### HEDIS Diabetes Care - Hemoglobin A1c
- **Denominator**: Members 18-75 years of age with diabetes
- **Numerator**: Members with most recent HbA1c < 8.0%
- **Measurement Period**: Calendar year

### HEDIS Breast Cancer Screening  
- **Denominator**: Women 50-74 years of age
- **Numerator**: Women with mammography within past 2 years
- **Measurement Period**: Calendar year

### HVBP Patient Safety Indicator - PSI-04
- **Denominator**: Surgical inpatients
- **Numerator**: Deaths among surgical inpatients
- **Measurement Period**: Calendar year

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

## Roadmap

- [ ] Additional HEDIS measures (Colorectal Cancer Screening, Cervical Cancer Screening)
- [ ] Additional HVBP measures (Clinical Process of Care, Patient Experience)
- [ ] Real-time data integration with Epic Clarity
- [ ] Advanced analytics and reporting dashboard
- [ ] FHIR R4 integration
- [ ] Machine learning for predictive quality measures