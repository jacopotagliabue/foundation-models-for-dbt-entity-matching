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
