SELECT 
    ltable_id::INT as A_ID,
    rtable_id::INT as B_ID,
    TO_BOOLEAN(label) AS LABEL
FROM {{ ref('test') }}