{{ config(materialized='table') }}

with patients as (
    select * from {{ ref('dim_patients') }}
),

diagnoses as (
    select * from {{ ref('stg_diagnoses') }}
),

lab_results as (
    select * from {{ source('raw_data', 'lab_results') }}
),

-- Identify diabetes patients
diabetes_patients as (
    select distinct patient_id
    from diagnoses
    where diagnosis_code like 'E10%' or diagnosis_code like 'E11%' or diagnosis_code like 'E12%' or diagnosis_code like 'E13%' or diagnosis_code like 'E14%'
),

-- Get A1C lab results
a1c_results as (
    select
        patient_id,
        result_value,
        result_date,
        -- Convert result_value to numeric for A1C
        case 
            when result_value ~ '^[0-9]+\.?[0-9]*$' then result_value::numeric
            else null
        end as a1c_value
    from lab_results
    where lab_code = 'A1C' or lab_name ilike '%hemoglobin a1c%'
),

-- Calculate measure
measure_calculation as (
    select
        p.patient_id,
        p.mrn,
        p.full_name,
        p.date_of_birth,
        p.age_years,
        -- Denominator: Diabetes patients 18-75 years old
        case 
            when dp.patient_id is not null and p.age_years >= 18 and p.age_years <= 75 then 1 
            else 0 
        end as denominator,
        -- Numerator: A1C < 8.0% within measurement year
        case 
            when dp.patient_id is not null 
                 and p.age_years >= 18 and p.age_years <= 75
                 and a1c.a1c_value < 8.0
                 and a1c.result_date >= date_trunc('year', current_date)
                 and a1c.result_date < date_trunc('year', current_date) + interval '1 year'
            then 1 
            else 0 
        end as numerator,
        a1c.a1c_value as most_recent_a1c,
        a1c.result_date as most_recent_a1c_date
    from patients p
    left join diabetes_patients dp on p.patient_id = dp.patient_id
    left join lateral (
        select a1c_value, result_date
        from a1c_results a
        where a.patient_id = p.patient_id
        and a.result_date >= date_trunc('year', current_date)
        and a.result_date < date_trunc('year', current_date) + interval '1 year'
        order by a.result_date desc
        limit 1
    ) a1c on true
)

select 
    patient_id,
    mrn,
    full_name,
    date_of_birth,
    age_years,
    denominator,
    numerator,
    most_recent_a1c,
    most_recent_a1c_date,
    current_date as measurement_date
from measure_calculation
where denominator = 1  -- Only include eligible patients