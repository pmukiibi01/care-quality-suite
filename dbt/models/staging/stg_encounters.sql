{{ config(materialized='view') }}

with source_data as (
    select * from {{ source('raw_data', 'encounters') }}
),

renamed as (
    select
        encounter_id,
        patient_id,
        encounter_type,
        admission_date,
        discharge_date,
        facility_id,
        provider_id,
        primary_diagnosis_code,
        created_at,
        -- Calculate length of stay in days
        case 
            when discharge_date is not null and admission_date is not null 
            then extract(epoch from (discharge_date - admission_date)) / 86400
            else null 
        end as length_of_stay_days
    from source_data
)

select * from renamed