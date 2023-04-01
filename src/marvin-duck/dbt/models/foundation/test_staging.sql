SELECT 
    ltable_id::INT as A_ID,
    rtable_id::INT as B_ID,
    label AS LABEL
FROM {{ ref('test') }}