{{ config(materialized='table') }}

with encounters as (
    select * from {{ ref('fact_encounters') }}
),

diagnoses as (
    select * from {{ ref('stg_diagnoses') }}
),

-- Identify PSI-04 (Death among surgical inpatients)
surgical_deaths as (
    select
        e.encounter_id,
        e.patient_id,
        e.admission_date,
        e.discharge_date,
        e.encounter_type,
        e.length_of_stay_days,
        -- Check for surgical procedures (simplified)
        case 
            when exists (
                select 1 from {{ source('raw_data', 'procedures') }} p
                where p.encounter_id = e.encounter_id
                and p.procedure_code in (
                    '0016T', '0017T', '0018T', '0019T', '0020T',  -- Surgical codes
                    '10021', '10040', '10060', '10080', '10120',  -- More surgical codes
                    '11000', '11010', '11011', '11012'            -- Additional surgical codes
                )
            ) then true 
            else false 
        end as has_surgical_procedure,
        -- Check for death (simplified - would need actual death data)
        case 
            when e.discharge_date is not null 
                 and e.encounter_type = 'Inpatient'
                 and e.length_of_stay_days > 1
                 and exists (
                     select 1 from diagnoses d
                     where d.encounter_id = e.encounter_id
                     and d.diagnosis_code in ('Z78.1', 'R99')  -- Death-related codes
                 )
            then true 
            else false 
        end as is_death
    from encounters e
    where e.encounter_type = 'Inpatient'
    and e.admission_date >= current_date - interval '1 year'
),

-- Calculate PSI-04 measure
psi_calculation as (
    select
        patient_id,
        encounter_id,
        admission_date,
        discharge_date,
        length_of_stay_days,
        -- Denominator: Surgical inpatients
        case 
            when has_surgical_procedure then 1 
            else 0 
        end as denominator,
        -- Numerator: Deaths among surgical inpatients
        case 
            when has_surgical_procedure and is_death then 1 
            else 0 
        end as numerator,
        has_surgical_procedure,
        is_death
    from surgical_deaths
)

select 
    patient_id,
    encounter_id,
    admission_date,
    discharge_date,
    length_of_stay_days,
    denominator,
    numerator,
    has_surgical_procedure,
    is_death,
    'PSI-04' as measure_id,
    'Death among surgical inpatients' as measure_name,
    current_date as measurement_date
from psi_calculation
where denominator = 1  -- Only include surgical patients