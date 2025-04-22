{{ config(materialized='table') }}

with encounters as (
    select * from {{ ref('stg_encounters') }}
),

-- Add encounter flags for quality measures
encounter_flags as (
    select
        *,
        case 
            when encounter_type in ('Inpatient', 'Emergency') then true 
            else false 
        end as is_inpatient_encounter,
        case 
            when encounter_type = 'Outpatient' then true 
            else false 
        end as is_outpatient_encounter,
        case 
            when length_of_stay_days > 30 then true 
            else false 
        end as is_extended_stay,
        -- Quality measure flags
        case 
            when encounter_type = 'Inpatient' and length_of_stay_days <= 4 then true 
            else false 
        end as is_short_stay,
        case 
            when encounter_type = 'Emergency' and discharge_date::date = admission_date::date then true 
            else false 
        end as is_same_day_ed_discharge
    from encounters
)

select * from encounter_flags