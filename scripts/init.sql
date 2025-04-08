-- Initialize the value-based care quality database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw_data;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS quality_measures;

-- Create sample tables for Epic Clarity/Caboodle data
CREATE TABLE IF NOT EXISTS raw_data.patients (
    patient_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mrn VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    gender VARCHAR(10),
    race VARCHAR(50),
    ethnicity VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_data.encounters (
    encounter_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES raw_data.patients(patient_id),
    encounter_type VARCHAR(50),
    admission_date TIMESTAMP,
    discharge_date TIMESTAMP,
    facility_id VARCHAR(50),
    provider_id VARCHAR(50),
    primary_diagnosis_code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_data.diagnoses (
    diagnosis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    encounter_id UUID REFERENCES raw_data.encounters(encounter_id),
    patient_id UUID REFERENCES raw_data.patients(patient_id),
    diagnosis_code VARCHAR(20),
    diagnosis_type VARCHAR(20),
    diagnosis_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_data.procedures (
    procedure_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    encounter_id UUID REFERENCES raw_data.encounters(encounter_id),
    patient_id UUID REFERENCES raw_data.patients(patient_id),
    procedure_code VARCHAR(20),
    procedure_date TIMESTAMP,
    provider_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_data.medications (
    medication_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES raw_data.patients(patient_id),
    medication_name VARCHAR(200),
    medication_code VARCHAR(20),
    prescription_date TIMESTAMP,
    provider_id VARCHAR(50),
    dosage VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_data.lab_results (
    lab_result_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES raw_data.patients(patient_id),
    lab_code VARCHAR(20),
    lab_name VARCHAR(200),
    result_value VARCHAR(200),
    result_date TIMESTAMP,
    reference_range VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create claims tables
CREATE TABLE IF NOT EXISTS raw_data.claims (
    claim_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES raw_data.patients(patient_id),
    claim_number VARCHAR(50),
    claim_type VARCHAR(20),
    service_date DATE,
    billing_provider_id VARCHAR(50),
    total_charges DECIMAL(10,2),
    total_paid DECIMAL(10,2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_data.claim_line_items (
    line_item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID REFERENCES raw_data.claims(claim_id),
    procedure_code VARCHAR(20),
    diagnosis_code VARCHAR(20),
    service_date DATE,
    units INTEGER,
    unit_charge DECIMAL(10,2),
    total_charge DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create payer roster table
CREATE TABLE IF NOT EXISTS raw_data.payer_rosters (
    roster_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES raw_data.patients(patient_id),
    payer_id VARCHAR(50),
    payer_name VARCHAR(200),
    member_id VARCHAR(50),
    effective_date DATE,
    termination_date DATE,
    plan_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_patients_mrn ON raw_data.patients(mrn);
CREATE INDEX IF NOT EXISTS idx_encounters_patient_id ON raw_data.encounters(patient_id);
CREATE INDEX IF NOT EXISTS idx_encounters_admission_date ON raw_data.encounters(admission_date);
CREATE INDEX IF NOT EXISTS idx_diagnoses_patient_id ON raw_data.diagnoses(patient_id);
CREATE INDEX IF NOT EXISTS idx_diagnoses_code ON raw_data.diagnoses(diagnosis_code);
CREATE INDEX IF NOT EXISTS idx_procedures_patient_id ON raw_data.procedures(patient_id);
CREATE INDEX IF NOT EXISTS idx_medications_patient_id ON raw_data.medications(patient_id);
CREATE INDEX IF NOT EXISTS idx_lab_results_patient_id ON raw_data.lab_results(patient_id);
CREATE INDEX IF NOT EXISTS idx_claims_patient_id ON raw_data.claims(patient_id);
CREATE INDEX IF NOT EXISTS idx_claims_service_date ON raw_data.claims(service_date);
CREATE INDEX IF NOT EXISTS idx_payer_rosters_patient_id ON raw_data.payer_rosters(patient_id);