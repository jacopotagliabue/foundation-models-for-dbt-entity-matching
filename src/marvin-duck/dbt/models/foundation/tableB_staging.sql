SELECT 
    id::INT as B_PRODUCT_ID,
    title::VARCHAR as B_PRODUCT_NAME,
    category::VARCHAR as B_CATEGORY,
    brand::VARCHAR AS B_BRAND,
    price::VARCHAR as B_PRICE -- we need to concatenate it later, so we are skipping a conversion
FROM {{ ref('tableB') }}