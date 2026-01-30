CREATE OR REPLACE TABLE gold_master_part_inventory AS
WITH reserved AS (
    -- Reserved quantities per plant + part
    SELECT
        plant_id,
        part_id,
        SUM(quantity) AS reserved_qty
    FROM raw_inventory_reservations
    GROUP BY plant_id, part_id
),

plant_coords AS (
    SELECT
        plant_id,
        name AS plant_name,
        lat,
        lon
    FROM raw_plants
),

part_names AS (
    SELECT
        part_id,
        name AS part_name
    FROM raw_parts
),

future_demand AS (
    -- Sum of future work order requirements per site + part
    SELECT
        plant_id,
        part_id,
        SUM(required_part_quantity) AS total_future_demand
    FROM raw_planned_maintenance
    WHERE planned_date >= CURRENT_DATE()
    GROUP BY plant_id, part_id
),

inventory_with_vendor AS (
    SELECT
        pi.*,
        COALESCE(r.reserved_qty,0) AS reserved_qty,
        COALESCE(fd.total_future_demand,0) AS total_future_demand,
        v.vendor_id,
        v.lead_time_days,
        v.min_order_quantity,
        ve.reliability
    FROM raw_parts_inventory pi
    LEFT JOIN reserved r
        ON pi.plant_id = r.plant_id AND pi.part_id = r.part_id
    LEFT JOIN future_demand fd
        ON pi.plant_id = fd.plant_id AND pi.part_id = fd.part_id
    LEFT JOIN raw_vendor_parts v
        ON pi.part_id = v.part_id
    LEFT JOIN raw_vendors as ve 
        ON v.vendor_id = ve.vendor_id
)

SELECT
    iwv.plant_id,
    pc.plant_name,
    pc.lat,
    pc.lon,
    iwv.part_id,
    pn.part_name,
    pm.equip_id,
    e.name AS equip_name,
    pm.work_order_id,
    pm.planned_date,
    pm.required_part_quantity,
    pm.criticality,
    iwv.on_hand_stock,
    iwv.reserved_qty,
    iwv.total_future_demand,
    -- Projected availability after reserved and work order
    (iwv.on_hand_stock - iwv.reserved_qty - COALESCE(pm.required_part_quantity,0)) AS projected_available_stock,
    -- Safety stock: 20% of on-hand, minimum 5
    GREATEST(iwv.on_hand_stock * 0.2, 5) AS safety_stock,
    -- Will this work order cause a breach?
    CASE
        WHEN (iwv.on_hand_stock - iwv.reserved_qty - COALESCE(pm.required_part_quantity,0)) < GREATEST(iwv.on_hand_stock * 0.2, 5) THEN TRUE
        ELSE FALSE
    END AS will_breach_safety_stock,
    -- Shortage quantity caused by work order
    GREATEST(GREATEST(iwv.on_hand_stock * 0.2,5) - (iwv.on_hand_stock - iwv.reserved_qty - COALESCE(pm.required_part_quantity,0)), 0) AS shortage_quantity,
    -- Risk level based on projected availability
    CASE
        WHEN (iwv.on_hand_stock - iwv.reserved_qty - COALESCE(pm.required_part_quantity,0)) < 0 THEN 'Out of Stock'
        WHEN (iwv.on_hand_stock - iwv.reserved_qty - COALESCE(pm.required_part_quantity,0)) < GREATEST(iwv.on_hand_stock * 0.2,5) THEN 'Low Stock'
        ELSE 'Stocked'
    END AS risk_level,
    -- Available for transfer to another site
    GREATEST(iwv.on_hand_stock - iwv.reserved_qty - GREATEST(iwv.on_hand_stock*0.2,5),0) AS available_for_transfer,
    iwv.vendor_id,
    iwv.lead_time_days,
    iwv.min_order_quantity,
    iwv.reliability
FROM inventory_with_vendor iwv
JOIN plant_coords pc
    ON iwv.plant_id = pc.plant_id
JOIN part_names pn
    ON iwv.part_id = pn.part_id
LEFT JOIN raw_planned_maintenance pm
    ON iwv.plant_id = pm.plant_id AND iwv.part_id = pm.part_id
    AND pm.planned_date >= CURRENT_DATE()
LEFT JOIN raw_equipment e
    ON pm.equip_id = e.equip_id
ORDER BY pc.plant_name, iwv.part_id, pm.planned_date;
