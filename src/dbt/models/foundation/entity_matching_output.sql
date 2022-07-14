WITH matching_input as 
(
    SELECT 
        *
    FROM 
        {{ ref('entity_matching_input')}} as em
    sample (1) seed (42) -- sample some test cases with a seed for reproducibility
    LIMIT 3 -- limit the number of rows for cost control!
)
SELECT 
    external_functions.lambda.resolution(em.SERIALIZED_A, em.SERIALIZED_B) as RESOLUTION,
    em.*
FROM 
    matching_input as em
