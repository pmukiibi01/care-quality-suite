{{ config(materialized='view') }}

with source_data as (
    select * from {{ source('raw_data', 'diagnoses') }}
),

renamed as (
    select
        diagnosis_id,
        encounter_id,
        patient_id,
        diagnosis_code,
        diagnosis_type,
        diagnosis_date,
        created_at,
        -- Create diagnosis category for grouping
        case 
            when diagnosis_code like 'E10%' or diagnosis_code like 'E11%' or diagnosis_code like 'E12%' or diagnosis_code like 'E13%' or diagnosis_code like 'E14%'
            then 'Diabetes'
            when diagnosis_code like 'I10%' or diagnosis_code like 'I11%' or diagnosis_code like 'I12%' or diagnosis_code like 'I13%' or diagnosis_code like 'I15%'
            then 'Hypertension'
            when diagnosis_code like 'C%' and diagnosis_code not like 'C9%'
            then 'Cancer'
            when diagnosis_code like 'F%'
            then 'Mental Health'
            else 'Other'
        end as diagnosis_category
    from source_data
)

select * from renamed