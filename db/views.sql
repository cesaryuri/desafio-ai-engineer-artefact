DROP VIEW IF EXISTS vw_catalogo_produtos;

CREATE VIEW vw_catalogo_produtos AS
SELECT
    p.product_id,
    p.name AS product_name,
    p.category_id,
    c.name AS category_name,
    p.price_brl AS original_price_brl,
    COALESCE(pr.discount_percent, 0) AS discount_percent,
    pr.description AS promotion_name,
    ROUND(p.price_brl * (1.0 - COALESCE(pr.discount_percent, 0) / 100.0), 2) AS final_price_brl,
    CASE
        WHEN pr.promotion_id IS NOT NULL THEN ROUND(p.price_brl * (1.0 - pr.discount_percent / 100.0), 2)
        ELSE ROUND(p.price_brl * 0.95, 2)
    END AS pix_price_brl,
    p.stock_quantity,
    p.status,
    CASE
        WHEN p.status = 'active' AND p.stock_quantity > 0 THEN 'disponivel'
        WHEN p.status = 'active' AND p.stock_quantity <= 0 THEN 'sem_estoque'
        WHEN p.status = 'coming_soon' THEN 'em_breve'
        ELSE 'descontinuado'
    END AS availability_status,
    p.strings,
    p.electronics,
    p.color,
    p.description,
    p.specs
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id
LEFT JOIN promotions pr ON p.product_id = pr.product_id AND pr.is_active = 1;


DROP VIEW IF EXISTS vw_pedidos_detalhados;

CREATE VIEW vw_pedidos_detalhados AS
SELECT
    o.order_id,
    o.order_date,
    o.status AS order_status,
    o.total_brl,
    o.payment_method,
    o.tracking_code,
    o.estimated_delivery,
    o.notes,
    cu.customer_id,
    cu.name AS customer_name,
    cu.phone AS customer_phone,
    cu.email AS customer_email,
    cu.city AS customer_city,
    oi.product_id,
    p.name AS product_name,
    oi.quantity,
    p.price_brl AS unit_price_brl
FROM orders o
JOIN customers cu ON o.customer_id = cu.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;
