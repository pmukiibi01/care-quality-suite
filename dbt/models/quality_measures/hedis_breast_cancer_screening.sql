{{ config(materialized='table') }}

with patients as (
    select * from {{ ref('dim_patients') }}
),

procedures as (
    select * from {{ source('raw_data', 'procedures') }}
),

-- Breast cancer screening procedures
screening_procedures as (
    select
        patient_id,
        procedure_date,
        procedure_code
    from procedures
    where procedure_code in (
        '77067',  -- Mammography, bilateral
        '77065',  -- Mammography, unilateral
        '77066',  -- Mammography, bilateral with CAD
        'G0202',  -- Screening mammography
        'G0204'   -- Screening mammography with CAD
    )
),

-- Get most recent screening for each patient
most_recent_screening as (
    select
        patient_id,
        max(procedure_date) as last_screening_date,
        count(*) as screening_count
    from screening_procedures
    group by patient_id
),

-- Calculate measure
measure_calculation as (
    select
        p.patient_id,
        p.mrn,
        p.full_name,
        p.date_of_birth,
        p.age_years,
        p.gender,
        -- Denominator: Women 50-74 years old
        case 
            when p.gender = 'Female' and p.age_years >= 50 and p.age_years <= 74 then 1 
            else 0 
        end as denominator,
        -- Numerator: Mammography within past 2 years
        case 
            when p.gender = 'Female' 
                 and p.age_years >= 50 and p.age_years <= 74
                 and ms.last_screening_date >= current_date - interval '2 years'
            then 1 
            else 0 
        end as numerator,
        ms.last_screening_date,
        ms.screening_count
    from patients p
    left join most_recent_screening ms on p.patient_id = ms.patient_id
)

select 
    patient_id,
    mrn,
    full_name,
    date_of_birth,
    age_years,
    gender,
    denominator,
    numerator,
    last_screening_date,
    screening_count,
    current_date as measurement_date
from measure_calculation
where denominator = 1  -- Only include eligible patients