CREATE DATABASE IF NOT EXISTS csc440_project;
USE csc440_project;

-- 1. MANUFACTURER
CREATE TABLE Manufacturer (
    manufacturer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- 2. SUPPLIER
CREATE TABLE Supplier (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- 3. CATEGORY
CREATE TABLE Category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- 4. INGREDIENT
CREATE TABLE Ingredient (
    ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    type ENUM('atomic', 'compound') NOT NULL
);

-- 5. PRODUCT
CREATE TABLE Product (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    standard_batch_size INT NOT NULL CHECK (standard_batch_size > 0),
    manufacturer_id INT NOT NULL,
    category_id INT NOT NULL,
    FOREIGN KEY (manufacturer_id) REFERENCES Manufacturer(manufacturer_id),
    FOREIGN KEY (category_id) REFERENCES Category(category_id)
);

-- 6. RECIPE (Bill of Materials)
CREATE TABLE Recipe (
    recipe_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    version INT NOT NULL,
    creation_date DATE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id),
    UNIQUE (product_id, version)
);

-- 7. INGREDIENT_BATCH (Ingredient Lots)
CREATE TABLE Ingredient_Batch (
    lot_number VARCHAR(50) PRIMARY KEY,
    ingredient_id INT NOT NULL,
    supplier_id INT NOT NULL,
    supplier_batch_id VARCHAR(50) NOT NULL,
    quantity_received DECIMAL(10,2) NOT NULL CHECK (quantity_received > 0),
    quantity_on_hand DECIMAL(10,2) NOT NULL CHECK (quantity_on_hand >= 0),
    cost_per_unit DECIMAL(10,2) NOT NULL CHECK (cost_per_unit >= 0),
    expiration_date DATE NOT NULL,
    receipt_date DATE NOT NULL,
    FOREIGN KEY (ingredient_id) REFERENCES Ingredient(ingredient_id),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id),
    CHECK (expiration_date >= DATE_ADD(receipt_date, INTERVAL 90 DAY)),
    CHECK (quantity_on_hand <= quantity_received),
    UNIQUE(ingredient_id, supplier_id, supplier_batch_id)
);

-- 8. PRODUCT_BATCH (Product Lots)
CREATE TABLE Product_Batch (
    lot_number VARCHAR(50) PRIMARY KEY,
    product_id INT NOT NULL,
    manufacturer_id INT NOT NULL,
    manufacturer_batch_id VARCHAR(50) NOT NULL,
    recipe_id INT NOT NULL,
    quantity_produced INT NOT NULL CHECK (quantity_produced > 0),
    total_cost DECIMAL(12,2) NOT NULL CHECK (total_cost >= 0),
    cost_per_unit DECIMAL(12,4) GENERATED ALWAYS AS (total_cost / quantity_produced) STORED,
    production_date DATE NOT NULL,
    expiration_date DATE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES Product(product_id),
    FOREIGN KEY (recipe_id) REFERENCES Recipe(recipe_id),
    FOREIGN KEY (manufacturer_id) REFERENCES Manufacturer(manufacturer_id),
    UNIQUE(product_id, manufacturer_id, manufacturer_batch_id)
);

-- 9. FORMULATION (Supplier's definition of compound ingredients)
CREATE TABLE Formulation (
    formulation_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    version INT NOT NULL,
    pack_size DECIMAL(10,2) NOT NULL CHECK (pack_size > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    effective_date_start DATE NOT NULL,
    effective_date_end DATE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredient(ingredient_id),
    UNIQUE (supplier_id, ingredient_id, version),
    CHECK (effective_date_end > effective_date_start)
);

-- 10. REQUIRES (M:N - Recipe <-> Ingredient)
CREATE TABLE REQUIRES (
    recipe_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    quantity_required DECIMAL(10,4) NOT NULL CHECK (quantity_required > 0),
    unit_of_measure VARCHAR(20) NOT NULL,
    PRIMARY KEY (recipe_id, ingredient_id),
    FOREIGN KEY (recipe_id) REFERENCES Recipe(recipe_id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredient(ingredient_id)
);

-- 11. SUPPLIES (M:N - Supplier <-> Ingredient)
CREATE TABLE SUPPLIES (
    supplier_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    PRIMARY KEY (supplier_id, ingredient_id),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredient(ingredient_id)
);

-- 12. CONTAINS_MATERIALS (M:N - Formulation <-> Atomic Ingredient Materials)
CREATE TABLE CONTAINS_MATERIALS (
    formulation_id INT NOT NULL,
    material_ingredient_id INT NOT NULL,
    quantity DECIMAL(10,4) NOT NULL CHECK (quantity > 0),
    unit_of_measure VARCHAR(20) NOT NULL,
    PRIMARY KEY (formulation_id, material_ingredient_id),
    FOREIGN KEY (formulation_id) REFERENCES Formulation(formulation_id),
    FOREIGN KEY (material_ingredient_id) REFERENCES Ingredient(ingredient_id)
);

-- 13. CONSUMES (M:N - Product_Batch <-> Ingredient_Batch for traceability)
CREATE TABLE CONSUMES (
    product_batch_lot_number VARCHAR(50) NOT NULL,
    ingredient_batch_lot_number VARCHAR(50) NOT NULL,
    quantity_consumed DECIMAL(10,2) NOT NULL CHECK (quantity_consumed > 0),
    PRIMARY KEY (product_batch_lot_number, ingredient_batch_lot_number),
    FOREIGN KEY (product_batch_lot_number) REFERENCES Product_Batch(lot_number),
    FOREIGN KEY (ingredient_batch_lot_number) REFERENCES Ingredient_Batch(lot_number)
);

-- Trigger : Prevent expired / insufficient ingredient consumption
DROP TRIGGER IF EXISTS trg_before_consumes_insert;
DELIMITER $$
CREATE TRIGGER trg_before_consumes_insert
BEFORE INSERT ON CONSUMES
FOR EACH ROW
BEGIN
    DECLARE available_qty DECIMAL(10,2);
    DECLARE lot_expiry DATE;

    SELECT quantity_on_hand, expiration_date
    INTO available_qty, lot_expiry
    FROM Ingredient_Batch
    WHERE lot_number = NEW.ingredient_batch_lot_number;

    IF available_qty IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ingredient batch does not exist.';
    END IF;

    IF CURDATE() > lot_expiry THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Expired lot: cannot consume.';
    END IF;

    IF available_qty < NEW.quantity_consumed THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient inventory.';
    END IF;
END$$
DELIMITER ;


-- Trigger : Update on hand quantity after consumption
DELIMITER $$
CREATE TRIGGER trg_after_consumes_insert
AFTER INSERT ON CONSUMES
FOR EACH ROW
BEGIN
    -- Subtract the consumed quantity from the on hand total
    UPDATE Ingredient_Batch
    SET quantity_on_hand = quantity_on_hand - NEW.quantity_consumed
    WHERE lot_number = NEW.ingredient_batch_lot_number;
END$$
DELIMITER ;

-- Trigger : Automatically compute the full INGREDIENT lot number
DROP TRIGGER IF EXISTS trg_before_ingredient_batch_insert;
DELIMITER $$
CREATE TRIGGER trg_before_ingredient_batch_insert
BEFORE INSERT ON Ingredient_Batch
FOR EACH ROW
BEGIN
    IF NEW.lot_number IS NULL OR NEW.lot_number = '' THEN
        SET NEW.lot_number = CONCAT(
            NEW.ingredient_id, '-', 
            NEW.supplier_id, '-', 
            NEW.supplier_batch_id
        );
    END IF;
END$$
DELIMITER ;

-- Trigger : Automatically compute the full PRODUCT lot number
DROP TRIGGER IF EXISTS trg_before_product_batch_insert;
DELIMITER $$
CREATE TRIGGER trg_before_product_batch_insert
BEFORE INSERT ON Product_Batch
FOR EACH ROW
BEGIN
    IF NEW.lot_number IS NULL OR NEW.lot_number = '' THEN
        SET NEW.lot_number = CONCAT(
            NEW.product_id, '-', 
            NEW.manufacturer_id, '-', 
            NEW.manufacturer_batch_id
        );
    END IF;
END$$
DELIMITER ;

-- Trigger : Initialize quantity_on_hand on new batch intake
DELIMITER $$
CREATE TRIGGER trg_before_ingredient_batch_insert_set_onhand
BEFORE INSERT ON Ingredient_Batch
FOR EACH ROW
BEGIN

    SET NEW.quantity_on_hand = NEW.quantity_received;
END$$
DELIMITER ;

-- Trigger : Only one active recipe per product
DROP TRIGGER IF EXISTS trg_before_recipe_insert_active;
DELIMITER $$
CREATE TRIGGER trg_before_recipe_insert_active
BEFORE INSERT ON Recipe
FOR EACH ROW
BEGIN
    IF NEW.is_active = TRUE THEN
        IF (SELECT COUNT(*) FROM Recipe 
            WHERE product_id = NEW.product_id 
              AND is_active = TRUE) > 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only one active recipe allowed per product.';
        END IF;
    END IF;
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_before_recipe_update_active;
DELIMITER $$
CREATE TRIGGER trg_before_recipe_update_active
BEFORE UPDATE ON Recipe
FOR EACH ROW
BEGIN
    IF NEW.is_active = TRUE AND OLD.is_active = FALSE THEN
        IF (SELECT COUNT(*) FROM Recipe 
            WHERE product_id = NEW.product_id 
              AND is_active = TRUE 
              AND recipe_id <> OLD.recipe_id) > 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only one active recipe allowed per product.';
        END IF;
    END IF;
END$$
DELIMITER ;

-- Trigger : Prevent overlapping formulation dates
DROP TRIGGER IF EXISTS trg_before_formulation_insert;
DELIMITER $$
CREATE TRIGGER trg_before_formulation_insert
BEFORE INSERT ON Formulation
FOR EACH ROW
BEGIN
    DECLARE overlap INT;

    SELECT COUNT(*)
    INTO overlap
    FROM Formulation
    WHERE supplier_id = NEW.supplier_id
      AND ingredient_id = NEW.ingredient_id
      AND (
            NEW.effective_date_start <= effective_date_end
        AND NEW.effective_date_end >= effective_date_start
      );

    IF overlap > 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Overlapping formulation effective dates are not allowed.';
    END IF;
END$$
DELIMITER ;

-- Trigger : Materials must be atomic & not self-included
DROP TRIGGER IF EXISTS trg_before_contains_materials_insert;
DELIMITER $$
CREATE TRIGGER trg_before_contains_materials_insert
BEFORE INSERT ON CONTAINS_MATERIALS
FOR EACH ROW
BEGIN
    DECLARE parent_ing INT;
    DECLARE material_type ENUM('atomic','compound');

    -- Get ingredient of the formulation
    SELECT ingredient_id INTO parent_ing
    FROM Formulation
    WHERE formulation_id = NEW.formulation_id;

    IF parent_ing = NEW.material_ingredient_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A compound ingredient cannot include itself.';
    END IF;

    SELECT type INTO material_type
    FROM Ingredient
    WHERE ingredient_id = NEW.material_ingredient_id;

    IF material_type <> 'atomic' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Formulation materials must be atomic ingredients.';
    END IF;
END$$
DELIMITER ;



-- Record Production Batch
DELIMITER $$
CREATE PROCEDURE sp_RecordProductionBatch (
    -- These inputs come from the user/application
    IN p_product_id INT,
    IN p_recipe_id INT,
    IN p_produced_units INT,
    IN p_manufacturer_id INT,
    IN p_manufacturer_batch_id VARCHAR(50),
    IN p_production_date DATE,
    IN p_expiration_date DATE
)
BEGIN

    -- Declare variables
    DECLARE new_product_lot_number VARCHAR(50);
    DECLARE calculated_total_cost DECIMAL(12, 2) DEFAULT 0.0;
    
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_ing_lot_number VARCHAR(50);
    DECLARE v_ing_quantity DECIMAL(10, 2);
    DECLARE v_ing_cost_per_unit DECIMAL(10, 2);

    DECLARE cur_ingredients CURSOR FOR 
        SELECT lot_number, quantity FROM temp_consumption_list;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

	-- Start the transaction
    START TRANSACTION;

    -- Create the product batch record
    SET new_product_lot_number = CONCAT(p_product_id, '-', p_manufacturer_id, '-', p_manufacturer_batch_id);
    
    INSERT INTO Product_Batch (
        lot_number, product_id, manufacturer_id, manufacturer_batch_id, 
        recipe_id, quantity_produced, total_cost, production_date, expiration_date
    ) VALUES (
        new_product_lot_number, p_product_id, p_manufacturer_id, p_manufacturer_batch_id,
        p_recipe_id, p_produced_units, 0.00, p_production_date, p_expiration_date
    );

    -- Loop through ingredients and consume them
    OPEN cur_ingredients;

    read_loop: LOOP
        FETCH cur_ingredients INTO v_ing_lot_number, v_ing_quantity;
        IF done THEN
            LEAVE read_loop;
        END IF;

        INSERT INTO CONSUMES (product_batch_lot_number, ingredient_batch_lot_number, quantity_consumed)
        VALUES (new_product_lot_number, v_ing_lot_number, v_ing_quantity);
        
        SELECT cost_per_unit INTO v_ing_cost_per_unit
        FROM Ingredient_Batch
        WHERE lot_number = v_ing_lot_number;
        
        SET calculated_total_cost = calculated_total_cost + (v_ing_cost_per_unit * v_ing_quantity);
        
    END LOOP;

    CLOSE cur_ingredients;

     -- Upsate the batch with the final cost
    UPDATE Product_Batch
    SET total_cost = calculated_total_cost
    WHERE lot_number = new_product_lot_number;
    
    -- Commit the transaction
    COMMIT;
    
    SELECT * FROM Product_Batch WHERE lot_number = new_product_lot_number;

END$$
DELIMITER ;

-- VIEW 1: Current Active Supplier Formulations
CREATE VIEW v_ActiveSupplierFormulations AS
SELECT 
    f.formulation_id,
    s.supplier_id,
    s.name AS supplier_name,
    i.ingredient_id,
    i.name AS ingredient_name,
    i.type AS ingredient_type,
    f.version,
    f.pack_size,
    f.unit_price,
    f.effective_date_start,
    f.effective_date_end
FROM Formulation f
JOIN Supplier s ON f.supplier_id = s.supplier_id
JOIN Ingredient i ON f.ingredient_id = i.ingredient_id
WHERE CURDATE() BETWEEN f.effective_date_start AND f.effective_date_end
   OR f.is_active = TRUE;

-- VIEW 2: Flattened Product BOM (Ingredient List)
CREATE VIEW v_FlattenedProductBOM AS
SELECT
    r.product_id,
    p.name AS product_name,
    i.ingredient_id AS final_ingredient_id,
    i.name AS final_ingredient_name,
    req.quantity_required AS final_quantity_per_unit,
    req.unit_of_measure
FROM Recipe r
JOIN Product p ON r.product_id = p.product_id
JOIN REQUIRES req ON r.recipe_id = req.recipe_id
JOIN Ingredient i ON req.ingredient_id = i.ingredient_id
WHERE 
    r.is_active = TRUE
    AND i.type = 'atomic'

UNION ALL

SELECT 
    r.product_id,
    p.name AS product_name,
    mat_ing.ingredient_id AS final_ingredient_id,
    mat_ing.name AS final_ingredient_name,
    (req.quantity_required * cm.quantity) AS final_quantity_per_unit, 
    cm.unit_of_measure
FROM Recipe r
JOIN Product p ON r.product_id = p.product_id
JOIN REQUIRES req ON r.recipe_id = req.recipe_id
JOIN Ingredient comp_ing ON req.ingredient_id = comp_ing.ingredient_id
JOIN v_ActiveSupplierFormulations f ON f.ingredient_id = comp_ing.ingredient_id
JOIN CONTAINS_MATERIALS cm ON cm.formulation_id = f.formulation_id
JOIN Ingredient mat_ing ON cm.material_ingredient_id = mat_ing.ingredient_id
WHERE 
    r.is_active = TRUE
    AND comp_ing.type = 'compound';