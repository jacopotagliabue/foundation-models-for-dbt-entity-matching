WITH matching_input as 
(
    (
        SELECT 
            1000000 AS A_ID,
            1000000 AS B_ID,
            TRUE AS LABEL,
            'Title: aleratec inc cd dvd shredder Brand: aleratec' AS SERIALIZED_A,
            'Title: aleratec dvd cd shredder xc 240145 black Brand: aleratec' AS SERIALIZED_B
    )
    UNION ALL
    (
        SELECT 
            *
        FROM 
            {{ ref('entity_matching_input')}} as em
        sample (1) seed (42) -- sample some test cases with a seed for reproducibility
        LIMIT 2 -- limit the number of rows for cost control!
    )
)
SELECT 
    external_functions.lambda.resolution(em.SERIALIZED_A, em.SERIALIZED_B) as RESOLUTION,
    em.*
FROM 
    matching_input as em
