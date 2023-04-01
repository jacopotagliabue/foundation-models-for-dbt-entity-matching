SELECT 
    ltable_id::INT as A_ID,
    rtable_id::INT as B_ID,
    CASE WHEN label=0 THEN FALSE ELSE TRUE END AS LABEL
FROM {{ ref('test') }}