SELECT 
    id::INT as A_PRODUCT_ID,
    title::VARCHAR as A_PRODUCT_NAME,
    LOWER(TRIM(split_part(category::VARCHAR, '-',  0))) as A_CATEGORY,
    brand::VARCHAR AS A_BRAND,
    price::VARCHAR as A_PRICE -- we need to concatenate it later, so we are skipping a conversion
FROM {{ ref('tableA') }}