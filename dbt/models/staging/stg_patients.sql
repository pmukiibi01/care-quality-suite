{{ config(materialized='view') }}

with source_data as (
    select * from {{ source('raw_data', 'patients') }}
),

renamed as (
    select
        patient_id,
        mrn,
        first_name,
        last_name,
        date_of_birth,
        gender,
        race,
        ethnicity,
        created_at,
        updated_at,
        -- Calculate age at measurement date
        extract(year from age(current_date, date_of_birth)) as age_years,
        -- Create full name
        concat(first_name, ' ', last_name) as full_name
    from source_data
)

select * from renamed