{{ config(materialized='table') }}

with patients as (
    select * from {{ ref('stg_patients') }}
),

-- Add demographic flags for quality measures
demographics as (
    select
        *,
        case 
            when age_years >= 18 and age_years <= 75 then true 
            else false 
        end as is_adult,
        case 
            when age_years >= 50 and age_years <= 75 then true 
            else false 
        end as is_colorectal_screening_age,
        case 
            when age_years >= 21 and age_years <= 64 then true 
            else false 
        end as is_cervical_screening_age,
        case 
            when age_years >= 50 and age_years <= 74 then true 
            else false 
        end as is_breast_cancer_screening_age,
        case 
            when gender = 'Female' and age_years >= 21 and age_years <= 64 then true 
            else false 
        end as is_cervical_screening_eligible,
        case 
            when gender = 'Female' and age_years >= 50 and age_years <= 74 then true 
            else false 
        end as is_breast_cancer_screening_eligible
    from patients
)

select * from demographics