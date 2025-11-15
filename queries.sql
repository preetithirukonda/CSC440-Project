USE csc440_project;

-- Disable foreign key checks temporarily for easier insertion
SET FOREIGN_KEY_CHECKS = 0;

-- 1. MANUFACTURERS
INSERT INTO Manufacturer (manufacturer_id, name) VALUES
(1, 'MFG001'),
(2, 'MFG002');


-- 2. SUPPLIERS
INSERT INTO Supplier (supplier_id, name) VALUES
(20, 'Supplier A'),
(21, 'Supplier B');

-- 3. CATEGORIES
INSERT INTO Category (category_id, name) VALUES
(2, 'Dinners'),
(3, 'Sides');

-- 4. INGREDIENTS
-- Atomic Ingredients
INSERT INTO Ingredient (ingredient_id, name, type) VALUES
(101, 'Salt', 'atomic'),
(102, 'Pepper', 'atomic'),
(104, 'Sodium Phosphate', 'atomic'),
(106, 'Beef Steak', 'atomic'),
(108, 'Pasta', 'atomic');

-- Compound Ingredients
INSERT INTO Ingredient (ingredient_id, name, type) VALUES
(201, 'Seasoning Blend', 'compound'),
(301, 'Super Seasoning', 'compound');

-- 5. SUPPLIES Relationship (Supplier -> Ingredient)
-- Supplier A (20) supplies these ingredients
INSERT INTO SUPPLIES (supplier_id, ingredient_id) VALUES
(20, 101),  -- Salt
(20, 106),  -- Beef Steak
(20, 108),  -- Pasta
(20, 201);  -- Seasoning Blend

-- Supplier B (21) supplies these ingredients
INSERT INTO SUPPLIES (supplier_id, ingredient_id) VALUES
(21, 102),  -- Pepper
(21, 104),  -- Sodium Phosphate
(21, 106),  -- Beef Steak
(21, 201),  -- Seasoning Blend
(21, 301);  -- Super Seasoning

-- 6. PRODUCTS
INSERT INTO Product (product_id, name, standard_batch_size, manufacturer_id, category_id) VALUES
(100, 'Steak Dinner', 100, 1, 2),   -- MFG001's Steak Dinner
(239, 'Mac & Cheese', 300, 1, 3),   -- MFG001's Mac & Cheese
(101, 'Steak Dinner', 50, 2, 2);    -- MFG002's Steak Dinner (different product_id than MFG001's)

-- 7. FORMULATIONS (Supplier definitions for ingredients)
INSERT INTO Formulation (formulation_id, supplier_id, ingredient_id, version, pack_size, unit_price, 
                        effective_date_start, effective_date_end, is_active) VALUES
-- Formulation 1: Salt from Supplier A
(1, 20, 101, 1, 8.0, 20.0, '2025-01-01', '2026-06-30', TRUE),

-- Formulation 2: Pepper from Supplier B
(2, 21, 102, 1, 5.0, 25.0, '2025-01-22', '2026-08-03', TRUE),

-- Formulation 3: Sodium Phosphate from Supplier B
(3, 21, 104, 1, 8.0, 30.0, '2025-01-01', '2026-01-01', TRUE),

-- Formulation 4: Beef Steak from Supplier B
(4, 21, 106, 1, 20.0, 100.0, '2025-01-01', '2026-06-30', TRUE),

-- Formulation 5: Beef Steak from Supplier A
(5, 20, 106, 1, 20.0, 90.0, '2025-04-10', '2026-10-10', TRUE),

-- Formulation 6: Pasta from Supplier A
(6, 20, 108, 1, 10.0, 50.0, '2025-05-28', '2026-03-28', TRUE),

-- Formulation 7: Seasoning Blend from Supplier B
(7, 21, 201, 1, 10.0, 5.0, '2025-07-17', '2026-01-17', TRUE),

-- Formulation 8: Seasoning Blend from Supplier A
(8, 20, 201, 1, 15.0, 5.0, '2025-09-25', '2026-07-25', TRUE),

-- Formulation 9: Super Seasoning from Supplier B
(9, 21, 301, 1, 6.0, 6.0, '2025-10-12', '2026-06-12', TRUE);

-- 8. CONTAINS_MATERIALS (Formulation breakdown - atomic ingredients only)
-- Formulation 7: Seasoning Blend (Supplier B) = Salt + Pepper
INSERT INTO CONTAINS_MATERIALS (formulation_id, material_ingredient_id, quantity, unit_of_measure) VALUES
(7, 101, 0.6, 'oz'),   -- Salt
(7, 102, 1.0, 'oz');   -- Pepper

-- Formulation 8: Seasoning Blend (Supplier A) = Salt + Pepper
INSERT INTO CONTAINS_MATERIALS (formulation_id, material_ingredient_id, quantity, unit_of_measure) VALUES
(8, 101, 1.0, 'oz'),   -- Salt
(8, 102, 1.0, 'oz');   -- Pepper

-- Formulation 9: Super Seasoning (Supplier B) = Salt + Pepper + Sodium Phosphate
INSERT INTO CONTAINS_MATERIALS (formulation_id, material_ingredient_id, quantity, unit_of_measure) VALUES
(9, 101, 0.6, 'oz'),   -- Salt
(9, 102, 1.0, 'oz'),   -- Pepper
(9, 104, 1.0, 'oz');   -- Sodium Phosphate

-- 9. RECIPES (Recipe Plans)
INSERT INTO Recipe (recipe_id, product_id, version, creation_date, is_active) VALUES
(1, 100, 1, '2025-01-01', TRUE),   -- MFG001 Steak Dinner (plan_id 1)
(2, 239, 1, '2025-01-01', TRUE),   -- MFG001 Mac & Cheese (plan_id 2)
(3, 101, 1, '2025-02-01', TRUE);   -- MFG002 Steak Dinner (plan_id 3)

-- 10. REQUIRES (Recipe Plan Lines - ingredient requirements per unit)
-- Recipe 1: MFG001 Steak Dinner (product_id 100)
INSERT INTO REQUIRES (recipe_id, ingredient_id, quantity_required, unit_of_measure) VALUES
(1, 106, 6.0, 'oz'),    -- Beef Steak
(1, 201, 0.2, 'oz'),    -- Seasoning Blend
(1, 101, 0.1, 'oz');    -- Salt

-- Recipe 2: MFG001 Mac & Cheese (product_id 239)
INSERT INTO REQUIRES (recipe_id, ingredient_id, quantity_required, unit_of_measure) VALUES
(2, 101, 0.1, 'oz'),    -- Salt
(2, 102, 2.0, 'oz'),    -- Pepper
(2, 108, 1.0, 'oz');    -- Pasta

-- Recipe 3: MFG002 Steak Dinner (product_id 101)
INSERT INTO REQUIRES (recipe_id, ingredient_id, quantity_required, unit_of_measure) VALUES
(3, 106, 6.0, 'oz'),    -- Beef Steak
(3, 201, 0.2, 'oz'),    -- Seasoning Blend
(3, 101, 0.1, 'oz');    -- Salt

-- 11. INGREDIENT BATCHES (Inventory Lots)
-- lot_number will be auto gen by trigger - ingredient_id-supplier_id-supplier_batch_id
-- quantity_on_hand will be set to quantity_received by trigger initially

-- Salt batches (ingredient 101)
INSERT INTO Ingredient_Batch (ingredient_id, supplier_id, supplier_batch_id, 
                              quantity_received, cost_per_unit, expiration_date, receipt_date) VALUES
(101, 20, 'B0001', 1000.00, 2.5, '2025-11-15', '2025-01-01'),
(101, 20, 'B0002', 500.00, 2.5, '2025-12-01', '2025-01-22'),
(101, 20, 'B0003', 500.00, 2.5, '2025-12-01', '2025-01-22');

-- Pepper batches (ingredient 102)
INSERT INTO Ingredient_Batch (ingredient_id, supplier_id, supplier_batch_id, 
                              quantity_received, cost_per_unit, expiration_date, receipt_date) VALUES
(102, 21, 'B0002', 1200.00, 5.0, '2025-12-15', '2025-06-03');

-- Sodium Phosphate batches (ingredient 104)
INSERT INTO Ingredient_Batch (ingredient_id, supplier_id, supplier_batch_id, 
                              quantity_received, cost_per_unit, expiration_date, receipt_date) VALUES
(104, 21, 'B0003', 250.00, 3.75, '2025-12-15', '2025-05-19');

-- Beef Steak batches (ingredient 106)
INSERT INTO Ingredient_Batch (ingredient_id, supplier_id, supplier_batch_id, 
                              quantity_received, cost_per_unit, expiration_date, receipt_date) VALUES
(106, 21, 'B0005', 3000.00, 5.0, '2025-12-15', '2025-06-12'),
(106, 20, 'B0006', 600.00, 4.5, '2025-12-20', '2025-01-22');

-- Pasta batches (ingredient 108)
INSERT INTO Ingredient_Batch (ingredient_id, supplier_id, supplier_batch_id, 
                              quantity_received, cost_per_unit, expiration_date, receipt_date) VALUES
-- (108, 20, 'B0007', 1000.00, 5.0, '2025-09-28', '2025-06-27'),
(108, 20, 'B0007', 1000.00, 5.0, '2025-12-28', '2025-06-27'),
(108, 20, 'B0008', 6300.00, 5.0, '2025-12-31', '2025-03-01');

-- Seasoning Blend batches (ingredient 201)
INSERT INTO Ingredient_Batch (ingredient_id, supplier_id, supplier_batch_id, 
                              quantity_received, cost_per_unit, expiration_date, receipt_date) VALUES
(201, 21, 'B0003', 100.00, 0.5, '2025-11-23', '2025-07-12'),
(201, 20, 'B0001', 150.00, 0.33, '2025-11-23', '2025-07-12');

-- Super Seasoning batches (ingredient 301)
INSERT INTO Ingredient_Batch (ingredient_id, supplier_id, supplier_batch_id, 
                              quantity_received, cost_per_unit, expiration_date, receipt_date) VALUES
(301, 21, 'B0004', 20.00, 1.0, '2025-11-30', '2025-04-01');

-- 12. PRODUCT BATCHES (Production Lots)
-- need to manually insert these and then add consumption records
-- lot_number will be auto gen by trigger - product_id-manufacturer_id-manufacturer_batch_id

-- Product Batch 1: MFG001 Steak Dinner (500 units produced)
INSERT INTO Product_Batch (product_id, manufacturer_id, manufacturer_batch_id, recipe_id, 
                           quantity_produced, total_cost, production_date, expiration_date) VALUES
(100, 1, 'B0901', 1, 500, 0.00, '2025-09-26', '2026-11-15');

-- Product Batch 2: MFG001 Mac & Cheese (300 units produced)
INSERT INTO Product_Batch (product_id, manufacturer_id, manufacturer_batch_id, recipe_id, 
                           quantity_produced, total_cost, production_date, expiration_date) VALUES
(239, 1, 'B0101', 2, 300, 0.00, '2025-09-10', '2026-10-30');

-- Product Batch 3: MFG002 Steak Dinner (50 units produced)
INSERT INTO Product_Batch (product_id, manufacturer_id, manufacturer_batch_id, recipe_id, 
                           quantity_produced, total_cost, production_date, expiration_date) VALUES
(101, 2, 'B0101', 3, 50, 0.00, '2025-09-10', '2025-12-10');

-- 13. PRODUCTION CONSUMPTION (Product Batch -> Ingredient Batch traceability)
-- Consumption for Product Batch 100-MFG001-B0901 (Steak Dinner, 500 units)
INSERT INTO CONSUMES (product_batch_lot_number, ingredient_batch_lot_number, quantity_consumed) VALUES
('100-1-B0901', '106-21-B0005', 3000.00),  -- Beef Steak (6 oz * 500 units)
('100-1-B0901', '201-21-B0003', 100.00),   -- Seasoning Blend (0.2 oz * 500)
('100-1-B0901', '101-20-B0002', 50.00);    -- Salt (0.1 oz * 500)

-- Consumption for Product Batch 239-MFG001-B0101 (Mac & Cheese, 300 units)
INSERT INTO CONSUMES (product_batch_lot_number, ingredient_batch_lot_number, quantity_consumed) VALUES
('239-1-B0101', '108-20-B0007', 300.00),   -- Pasta (1 oz * 300 units)
('239-1-B0101', '102-21-B0002', 600.00),   -- Pepper (2 oz * 300)
('239-1-B0101', '101-20-B0001', 30.00);    -- Salt (0.1 oz * 300)

-- Consumption for Product Batch 100-MFG002-B0101 (Steak Dinner, 50 units)
INSERT INTO CONSUMES (product_batch_lot_number, ingredient_batch_lot_number, quantity_consumed) VALUES
('101-2-B0101', '106-20-B0006', 300.00),   -- Beef Steak (6 oz * 50 units)
('101-2-B0101', '201-20-B0001', 10.00),    -- Seasoning Blend (0.2 oz * 50)
('101-2-B0101', '101-20-B0003', 5.00);     -- Salt (0.1 oz * 50)

-- UPDATE PRODUCT BATCH COSTS
-- Calculate and update total costs for each product batch based on actual consumption

-- Product Batch 100-MFG001-B0901
-- 3000 oz * 5.0 = 15000 + 100 oz * 0.5 = 50 + 50 oz * 2.5 = 125 = Total: 15175
UPDATE Product_Batch 
SET total_cost = 15175.00
WHERE lot_number = '100-1-B0901';

-- Product Batch 239-MFG001-B0101
-- 300 oz * 5.0 = 1500 + 600 oz * 5.0 = 3000 + 30 oz * 2.5 = 75 = Total: 4575
UPDATE Product_Batch 
SET total_cost = 4575.00
WHERE lot_number = '239-1-B0101';

-- Product Batch 100-MFG002-B0101
-- 300 oz * 4.5 = 1350 + 10 oz * 0.33 = 3.3 + 5 oz * 2.5 = 12.5 = Total: 1365.8
UPDATE Product_Batch 
SET total_cost = 1365.80
WHERE lot_number = '101-2-B0101';

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- VERIFICATION QUERIES
SELECT 'Data insertion completed successfully!' AS Status;

-- Show summary counts
SELECT 'Table Summary' AS Report_Type;
SELECT 'Manufacturers' AS Table_Name, COUNT(*) AS Record_Count FROM Manufacturer
UNION ALL
SELECT 'Suppliers', COUNT(*) FROM Supplier
UNION ALL
SELECT 'Categories', COUNT(*) FROM Category
UNION ALL
SELECT 'Ingredients', COUNT(*) FROM Ingredient
UNION ALL
SELECT 'Products', COUNT(*) FROM Product
UNION ALL
SELECT 'Recipes', COUNT(*) FROM Recipe
UNION ALL
SELECT 'Formulations', COUNT(*) FROM Formulation
UNION ALL
SELECT 'Ingredient_Batches', COUNT(*) FROM Ingredient_Batch
UNION ALL
SELECT 'Product_Batches', COUNT(*) FROM Product_Batch
UNION ALL
SELECT 'Consumptions', COUNT(*) FROM CONSUMES;

-- Show current inventory with on-hand quantities
SELECT 
    'Current Inventory' AS Report_Type;
    
SELECT 
    i.name AS Ingredient,
    ib.lot_number AS Lot_Number,
    ib.quantity_on_hand AS On_Hand,
    ib.quantity_received AS Original_Qty,
    ib.expiration_date AS Expires,
    s.name AS Supplier
FROM Ingredient_Batch ib
JOIN Ingredient i ON ib.ingredient_id = i.ingredient_id
JOIN Supplier s ON ib.supplier_id = s.supplier_id
ORDER BY i.name, ib.lot_number;

-- Show product batches with costs
SELECT 
    'Product Batches' AS Report_Type;
    
SELECT 
    pb.lot_number AS Lot_Number,
    p.name AS Product,
    m.name AS Manufacturer,
    pb.quantity_produced AS Qty_Produced,
    pb.total_cost AS Total_Cost,
    pb.cost_per_unit AS Cost_Per_Unit,
    pb.production_date AS Produced_On
FROM Product_Batch pb
JOIN Product p ON pb.product_id = p.product_id
JOIN Manufacturer m ON pb.manufacturer_id = m.manufacturer_id
ORDER BY pb.production_date DESC;

-- Show Recipe Plans and their ingredients
SELECT 
    'Recipe Plans' AS Report_Type;
    
SELECT 
    r.recipe_id AS Recipe_ID,
    p.name AS Product,
    m.name AS Manufacturer,
    i.name AS Ingredient,
    req.quantity_required AS Qty_Per_Unit,
    req.unit_of_measure AS Unit
FROM Recipe r
JOIN Product p ON r.product_id = p.product_id
JOIN Manufacturer m ON p.manufacturer_id = m.manufacturer_id
JOIN REQUIRES req ON r.recipe_id = req.recipe_id
JOIN Ingredient i ON req.ingredient_id = i.ingredient_id
WHERE r.is_active = TRUE
ORDER BY r.recipe_id, i.name;