WITH entity_matching  AS 
(
    SELECT 
    t.*,
    'Title: ' || a.A_PRODUCT_NAME  || ' Brand: ' || IFNULL(a.A_BRAND, '')  AS SERIALIZED_A,
    'Title: ' || b.B_PRODUCT_NAME  || ' Brand: ' || IFNULL(b.B_BRAND, '')  AS SERIALIZED_B
FROM 
    {{ ref('test_staging')}} as t
JOIN    
    {{ ref('tableA_staging') }} as a on a.A_PRODUCT_ID=t.A_ID
JOIN    
    {{ ref('tableB_staging') }} as b on b.B_PRODUCT_ID=t.B_ID
)
SELECT * FROM 
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
        SELECT  * FROM  entity_matching as em
        USING SAMPLE 50% 
        (system, 42) -- sample some test cases with a seed for reproducibility
        LIMIT 5 -- limit the number of rows for cost control!
    )
)
