import sys
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
from decimal import Decimal


class InventoryManagementSystem:
   def __init__(self):
       self.connection = None
       self.cursor = None
       self.current_user = None
       self.current_role = None
      
# connects to workbench databse
# usrname: root
# password: different for everyone
   def connect_to_database(self):
       print("DATABASE CONNECTION")
       print("---------------------------------------------------------------------------------------\n")
      
       try:
           host = input("Enter database host [localhost]: ").strip() or "localhost"
           database = input("Enter database name [csc440_project]: ").strip() or "csc440_project"
           user = input("Enter database username: ").strip()
           password = input("Enter database password: ").strip()
          
           self.connection = mysql.connector.connect(
               host=host,
               database=database,
               user=user,
               password=password
           )
          
           if self.connection.is_connected():
               self.cursor = self.connection.cursor(dictionary=True)
               print("\nSuccessfully connected to database!")
               return True
              
       except Error as e:
           print(f"\nError connecting to database: {e}")
           return False
  
   def close_connection(self):
       if self.cursor:
           self.cursor.close()
       if self.connection and self.connection.is_connected():
           self.connection.close()
           print("\nDatabase connection closed.")
  
   def login(self):
       print("\nINVENTORY MANAGEMENT SYSTEM - LOGIN")
       print("---------------------------------------------------------------------------------------\n")
       print("\nSelect Role:")
       print("  [1] Manufacturer")
       print("  [2] Supplier")
       print("  [3] General (Viewer)")
       print("  [4] Exit")
      
       choice = input("\nEnter choice (1-4): ").strip()
      
       if choice == '1':
           self.manufacturer_login()
       elif choice == '2':
           self.supplier_login()
       elif choice == '3':
           self.viewer_login()
       elif choice == '4':
           return False
       else:
           print("Invalid choice. Please try again.")
           return self.login()
      
       return True
  
   def manufacturer_login(self):
       print("\n----------- Manufacturer Login -----------")
       manufacturer_id = input("Enter Manufacturer ID (e.g., MFG001): ").strip()
      
       # verify that the manufacturer exists
       query = "SELECT manufacturer_id, name FROM Manufacturer WHERE name = %s"
       self.cursor.execute(query, (manufacturer_id,))
       result = self.cursor.fetchone()
      
       if result:
           self.current_user = result['manufacturer_id']
           self.current_role = 'MANUFACTURER'
           print(f"\nWelcome, {manufacturer_id}!")
           self.manufacturer_menu()
       else:
           print(f"\nManufacturer {manufacturer_id} not found.")
           self.login()
  
   def supplier_login(self):
       print("\n----------- Supplier Login -----------")
       supplier_id = input("Enter Supplier ID (e.g., 20, 21): ").strip()
      
       # Verify supplier exists
       query = "SELECT supplier_id, name FROM Supplier WHERE supplier_id = %s"
       self.cursor.execute(query, (supplier_id,))
       result = self.cursor.fetchone()
      
       if result:
           self.current_user = result['supplier_id']
           self.current_role = 'SUPPLIER'
           print(f"\nWelcome, {result['name']}!")
           self.supplier_menu()
       else:
           print(f"\nSupplier {supplier_id} not found.")
           self.login()
  
   def viewer_login(self):
       print("\nLogged in as Viewer (Read-only access)")
       self.current_role = 'VIEWER'
       self.viewer_menu()
  
#   manufacturer menu and functionality
   def manufacturer_menu(self):
       while True:
           
           print("\nMANUFACTURER MENU")
           print("---------------------------------------------------------------------------------------\n")
           print("  [1] Define/Update Product")
           print("  [2] Define/Update Recipe Plan")
           print("  [3] Record Ingredient Receipt")
           print("  [4] Create Product Batch")
           print("  [5] Reports")
           print("  [6] Run Required Queries")
           print("  [0] Logout")
          
           choice = input("\nEnter choice: ").strip()
          
           if choice == '1':
               self.define_update_product()
           elif choice == '2':
               self.define_update_recipe()
           elif choice == '3':
               self.record_ingredient_receipt()
           elif choice == '4':
               self.create_product_batch()
           elif choice == '5':
               self.manufacturer_reports()
           elif choice == '6':
               self.run_required_queries()
           elif choice == '0':
               break
           else:
               print("Invalid choice. Please try again.")
  
   def define_update_product(self):
       print("\n----------- Define/Update Product -----------")
       print("  [1] Create New Product")
       print("  [2] Update Existing Product")
       print("  [3] View My Products")
      
       choice = input("\nEnter choice: ").strip()
      
       if choice == '1':
           self.create_product()
       elif choice == '2':
           self.update_product()
       elif choice == '3':
           self.view_products()
  
   def create_product(self):
       print("\n----------- Create New Product -----------")
      

       self.cursor.execute("SELECT category_id, name FROM Category")
       categories = self.cursor.fetchall()
       print("\nAvailable Categories:")
       for cat in categories:
           print(f"  [{cat['category_id']}] {cat['name']}")
      
       try:
           product_name = input("\nProduct Name: ").strip()
           category_id = int(input("Category ID: ").strip())
           standard_batch_size = int(input("Standard Batch Size (units): ").strip())
          
           if standard_batch_size <= 0:
               print("Standard batch size must be positive.")
               return
          
           query = """
               INSERT INTO Product (name, standard_batch_size, manufacturer_id, category_id)
               VALUES (%s, %s, %s, %s)
           """
           self.cursor.execute(query, (product_name, standard_batch_size,
                                      self.current_user, category_id))
           self.connection.commit()
          
           print(f"\nProduct '{product_name}' created successfully!")
           print(f"  Product ID: {self.cursor.lastrowid}")
          
       except Error as e:
           print(f"\nError creating product: {e}")
           self.connection.rollback()
  
   def update_product(self):
       self.view_products()
      
       try:
           product_id = int(input("\nEnter Product ID to update: ").strip())
          
           # verify ownership of prod
           query = """
               SELECT * FROM Product
               WHERE product_id = %s AND manufacturer_id = %s
           """
           self.cursor.execute(query, (product_id, self.current_user))
           product = self.cursor.fetchone()
          
           if not product:
               print("Product not found or you don't have permission to update it.")
               return
          
           print(f"\nCurrent: {product['name']} - Batch Size: {product['standard_batch_size']}")
           new_batch_size = input("New Standard Batch Size (press Enter to keep current): ").strip()
          
           if new_batch_size:
               query = "UPDATE Product SET standard_batch_size = %s WHERE product_id = %s"
               self.cursor.execute(query, (int(new_batch_size), product_id))
               self.connection.commit()
               print("Product updated successfully!")
              
       except Error as e:
           print(f"\nError updating product: {e}")
           self.connection.rollback()
  
   def view_products(self):
       query = """
           SELECT p.product_id, p.name, c.name AS category, p.standard_batch_size
           FROM Product p
           JOIN Category c ON p.category_id = c.category_id
           WHERE p.manufacturer_id = %s
       """
       self.cursor.execute(query, (self.current_user,))
       products = self.cursor.fetchall()
      
       if products:
           print("\n----------- Your Products -----------")
           print(f"{'ID':<6} {'Name':<25} {'Category':<15} {'Batch Size'}")
           print("-" * 60)
           for p in products:
               print(f"{p['product_id']:<6} {p['name']:<25} {p['category']:<15} {p['standard_batch_size']}")
       else:
           print("\nNo products found.")
  
   def define_update_recipe(self):
       print("\n----------- Define/Update Recipe Plan -----------")
       self.view_products()
      
       try:
           product_id = int(input("\nEnter Product ID for recipe: ").strip())
          
           # verify ownership of prod
           query = "SELECT * FROM Product WHERE product_id = %s AND manufacturer_id = %s"
           self.cursor.execute(query, (product_id, self.current_user))
           product = self.cursor.fetchone()
          
           if not product:
               print("Product not found or access denied.")
               return
          
           # get tge current version
           query = "SELECT MAX(version) as max_ver FROM Recipe WHERE product_id = %s"
           self.cursor.execute(query, (product_id,))
           result = self.cursor.fetchone()
           new_version = (result['max_ver'] or 0) + 1
          
           # create a new recipe version
           query = """
               INSERT INTO Recipe (product_id, version, creation_date, is_active)
               VALUES (%s, %s, CURDATE(), FALSE)
           """
           self.cursor.execute(query, (product_id, new_version))
           recipe_id = self.cursor.lastrowid
          
           print(f"\nCreated Recipe Version {new_version}")
           print("Now add ingredients to this recipe...")
          

           self.add_recipe_ingredients(recipe_id)
          
           # see if this should be active
           activate = input("\nSet this as active recipe? (y/n): ").strip().lower()
           if activate == 'y':
               # rem/deactivate all other recipes for this product
               query = "UPDATE Recipe SET is_active = FALSE WHERE product_id = %s"
               self.cursor.execute(query, (product_id,))
              
               # and activate just this one
               query = "UPDATE Recipe SET is_active = TRUE WHERE recipe_id = %s"
               self.cursor.execute(query, (recipe_id,))
          
           self.connection.commit()
           print("\nRecipe plan created successfully!")
          
       except Error as e:
           print(f"\nError creating recipe: {e}")
           self.connection.rollback()
  
   def add_recipe_ingredients(self, recipe_id):
       # see all available ingredients
       self.cursor.execute("SELECT ingredient_id, name, type FROM Ingredient ORDER BY name")
       ingredients = self.cursor.fetchall()
      
       print("\nAvailable Ingredients:")
       for ing in ingredients:
           print(f"  [{ing['ingredient_id']}] {ing['name']} ({ing['type']})")
      
       while True:
           try:
               print("\nAdd ingredient (or 'done' to finish):")
               ing_input = input("Ingredient ID: ").strip()
              
               if ing_input.lower() == 'done':
                   break
              
               ing_id = int(ing_input)
               quantity = float(input("Quantity per unit (oz): ").strip())
              
               query = """
                   INSERT INTO REQUIRES (recipe_id, ingredient_id, quantity_required, unit_of_measure)
                   VALUES (%s, %s, %s, 'oz')
               """
               self.cursor.execute(query, (recipe_id, ing_id, quantity))
               print("Ingredient added to recipe")
              
           except ValueError:
               print("Invalid input. Please enter numeric values.")
           except Error as e:
               print(f"Error: {e}")
  
   def record_ingredient_receipt(self):
       print("\n----------- Record Ingredient Receipt -----------")
      
       # see all available ingredients
       self.cursor.execute("SELECT ingredient_id, name FROM Ingredient ORDER BY name")
       ingredients = self.cursor.fetchall()
      
       print("\nAvailable Ingredients:")
       for ing in ingredients:
           print(f"  [{ing['ingredient_id']}] {ing['name']}")
      
       try:
           ingredient_id = int(input("\nIngredient ID: ").strip())
           supplier_id = int(input("Supplier ID: ").strip())
           batch_id = input("Batch ID (e.g., B0001): ").strip()
           quantity = float(input("Quantity (oz): ").strip())
           cost_per_unit = float(input("Cost per unit (oz): ").strip())
           expiration_str = input("Expiration Date (YYYY-MM-DD): ").strip()
          
           # make sure expiration date is valid - today + 90 days should be bigger than that
           expiration_date = datetime.strptime(expiration_str, "%Y-%m-%d").date()
           min_expiration = datetime.now().date() + timedelta(days=90)
          
           if expiration_date < min_expiration:
               print(f"\nExpiration date must be at least 90 days from today ({min_expiration})")
               return
          
           # insert the ingredient batch
           query = """
               INSERT INTO Ingredient_Batch
               (ingredient_id, supplier_id, supplier_batch_id, quantity_received,
                cost_per_unit, expiration_date, receipt_date)
               VALUES (%s, %s, %s, %s, %s, %s, CURDATE())
           """
           self.cursor.execute(query, (ingredient_id, supplier_id, batch_id,
                                      quantity, cost_per_unit, expiration_date))
           self.connection.commit()
          
           lot_number = f"{ingredient_id}-{supplier_id}-{batch_id}"
           print(f"\nIngredient batch received successfully!")
           print(f"  Lot Number: {lot_number}")
           print(f"  Quantity: {quantity} oz")
          
       except ValueError:
           print("\n Invalid input format.")
       except Error as e:
           print(f"\nError recording receipt: {e}")
           self.connection.rollback()
  
   def create_product_batch(self):
       print("\n----------- Create Product Batch -----------")
       self.view_products()
      
       try:
           product_id = int(input("\nEnter Product ID: ").strip())
          
           # verify ownership of prod and get  the details
           query = """
               SELECT p.*, r.recipe_id, r.version
               FROM Product p
               LEFT JOIN Recipe r ON p.product_id = r.product_id AND r.is_active = TRUE
               WHERE p.product_id = %s AND p.manufacturer_id = %s
           """
           self.cursor.execute(query, (product_id, self.current_user))
           product = self.cursor.fetchone()
          
           if not product:
               print("Product not found or access denied.")
               return
          
           if not product['recipe_id']:
               print("No active recipe plan found for this product.")
               return
          
           print(f"\nProduct: {product['name']}")
           print(f"Standard Batch Size: {product['standard_batch_size']} units")
           print(f"Active Recipe Version: {product['version']}")
          
           query = """
               SELECT r.ingredient_id, i.name, r.quantity_required
               FROM REQUIRES r
               JOIN Ingredient i ON r.ingredient_id = i.ingredient_id
               WHERE r.recipe_id = %s
           """
           self.cursor.execute(query, (product['recipe_id'],))
           requirements = self.cursor.fetchall()
          
           print("\nRecipe Requirements (per unit):")
           for req in requirements:
               print(f"  {req['name']}: {req['quantity_required']} oz")
          
           # quantity
           produced_units = int(input("\nProduced Units: ").strip())
          
           # multiple of standard batch size ?
           if produced_units % product['standard_batch_size'] != 0:
               print(f"Produced units must be a multiple of {product['standard_batch_size']}")
               return
          
           manufacturer_batch_id = input("Manufacturer Batch ID (e.g., B0901): ").strip()
           expiration_str = input("Expiration Date (YYYY-MM-DD): ").strip()
           expiration_date = datetime.strptime(expiration_str, "%Y-%m-%d").date()
          
           print("\n----------- Select Ingredient Lots -----------")
           consumption_list = []
          
           for req in requirements:
               needed_qty = req['quantity_required'] * produced_units
               print(f"\n{req['name']}: Need {needed_qty} oz")
              
               query = """
                   SELECT lot_number, quantity_on_hand, expiration_date, cost_per_unit
                   FROM Ingredient_Batch
                   WHERE ingredient_id = %s AND quantity_on_hand > 0
                   ORDER BY expiration_date
               """
               self.cursor.execute(query, (req['ingredient_id'],))
               lots = self.cursor.fetchall()
              
               if not lots:
                   print(f"No inventory available for {req['name']}")
                   return
              
               print("Available Lots:")
               for lot in lots:
                   print(f"  {lot['lot_number']}: {lot['quantity_on_hand']} oz "
                         f"(expires: {lot['expiration_date']})")
              
               lot_number = input(f"Select lot number: ").strip()
              
               consumption_list.append({
                   'lot_number': lot_number,
                   'quantity': needed_qty
               })
          
           # create batch
           print("\nCreating production batch...")
           self.create_batch_with_procedure(product_id, product['recipe_id'],
                                           produced_units, self.current_user,
                                           manufacturer_batch_id, expiration_date,
                                           consumption_list)
          
       except ValueError:
           print("\nInvalid input format.")
       except Error as e:
           print(f"\nError creating product batch: {e}")
           self.connection.rollback()
  
   def create_batch_with_procedure(self, product_id, recipe_id, produced_units,
                                   manufacturer_id, batch_id, expiration_date,
                                   consumption_list):
       try:
           # temp table for consumption
           self.cursor.execute("DROP TEMPORARY TABLE IF EXISTS temp_consumption_list")
           self.cursor.execute("""
               CREATE TEMPORARY TABLE temp_consumption_list (
                   lot_number VARCHAR(50),
                   quantity DECIMAL(10,2)
               )
           """)

           for item in consumption_list:
               self.cursor.execute(
                   "INSERT INTO temp_consumption_list VALUES (%s, %s)",
                   (item['lot_number'], item['quantity'])
               )

           args = [product_id, recipe_id, produced_units, manufacturer_id,
                  batch_id, datetime.now().date(), expiration_date]
          
           self.cursor.callproc('sp_RecordProductionBatch', args)

           for result in self.cursor.stored_results():
               batch = result.fetchone()
               if batch:
                   print("\nProduct batch created successfully!")
                   print(f"  Lot Number: {batch['lot_number']}")
                   print(f"  Quantity: {batch['quantity_produced']} units")
                   print(f"  Total Cost: ${batch['total_cost']:.2f}")
                   print(f"  Cost Per Unit: ${batch['cost_per_unit']:.4f}")
          
           self.connection.commit()
          
       except Error as e:
           print(f"\nError: {e}")
           self.connection.rollback()
  
   def manufacturer_reports(self):
       while True:
           print("\n----------- Reports Menu -----------")
           print("  [1] On-hand Inventory by Item/Lot")
           print("  [2] Nearly Out of Stock")
           print("  [3] Almost Expired Ingredients")
           print("  [4] Batch Cost Summary")
           print("  [0] Back")
          
           choice = input("\nEnter choice: ").strip()
          
           if choice == '1':
               self.report_onhand_inventory()
           elif choice == '2':
               self.report_nearly_out_of_stock()
           elif choice == '3':
               self.report_almost_expired()
           elif choice == '4':
               self.report_batch_cost()
           elif choice == '0':
               break
  
   def report_onhand_inventory(self):
       print("\n----------- On-Hand Inventory -----------")
      
       query = """
           SELECT
               i.name AS ingredient,
               ib.lot_number,
               ib.quantity_on_hand,
               ib.expiration_date,
               s.name AS supplier
           FROM Ingredient_Batch ib
           JOIN Ingredient i ON ib.ingredient_id = i.ingredient_id
           JOIN Supplier s ON ib.supplier_id = s.supplier_id
           WHERE ib.quantity_on_hand > 0
           ORDER BY i.name, ib.expiration_date
       """
       self.cursor.execute(query)
       inventory = self.cursor.fetchall()
      
       if inventory:
           print(f"\n{'Ingredient':<20} {'Lot Number':<20} {'On-Hand':<12} {'Expires':<12} {'Supplier'}")
           print("-" * 90)
           for item in inventory:
               print(f"{item['ingredient']:<20} {item['lot_number']:<20} "
                     f"{item['quantity_on_hand']:<12.2f} {str(item['expiration_date']):<12} "
                     f"{item['supplier']}")
       else:
           print("\nNo inventory on hand.")
  
   def report_nearly_out_of_stock(self):
       print("\n----------- Nearly Out of Stock -----------")
       print("(Items with on-hand quantity < needed for one batch)")
      
       query = """
           SELECT
               p.name AS product,
               p.standard_batch_size,
               i.name AS ingredient,
               req.quantity_required,
               COALESCE(SUM(ib.quantity_on_hand), 0) AS total_on_hand,
               (p.standard_batch_size * req.quantity_required) AS needed_for_batch
           FROM Product p
           JOIN Recipe r ON p.product_id = r.product_id AND r.is_active = TRUE
           JOIN REQUIRES req ON r.recipe_id = req.recipe_id
           JOIN Ingredient i ON req.ingredient_id = i.ingredient_id
           LEFT JOIN Ingredient_Batch ib ON i.ingredient_id = ib.ingredient_id
           WHERE p.manufacturer_id = %s
           GROUP BY p.product_id, p.name, p.standard_batch_size,
                    i.ingredient_id, i.name, req.quantity_required
           HAVING total_on_hand < needed_for_batch
           ORDER BY p.name, i.name
       """
       self.cursor.execute(query, (self.current_user,))
       items = self.cursor.fetchall()
      
       if items:
           print(f"\n{'Product':<25} {'Ingredient':<20} {'On-Hand':<12} {'Needed':<12}")
           print("-" * 75)
           for item in items:
               print(f"{item['product']:<25} {item['ingredient']:<20} "
                     f"{item['total_on_hand']:<12.2f} {item['needed_for_batch']:<12.2f}")
       else:
           print("\nAll items are adequately stocked.")
  
   def report_almost_expired(self):
       print("\n----------- Almost Expired Ingredients (within 10 days) -----------")
      
       query = """
           SELECT
               i.name AS ingredient,
               ib.lot_number,
               ib.quantity_on_hand,
               ib.expiration_date,
               DATEDIFF(ib.expiration_date, CURDATE()) AS days_until_expiry
           FROM Ingredient_Batch ib
           JOIN Ingredient i ON ib.ingredient_id = i.ingredient_id
           WHERE ib.quantity_on_hand > 0
             AND ib.expiration_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 10 DAY)
           ORDER BY ib.expiration_date
       """
       self.cursor.execute(query)
       items = self.cursor.fetchall()
      
       if items:
           print(f"\n{'Ingredient':<20} {'Lot Number':<20} {'On-Hand':<12} {'Expires':<12} {'Days Left'}")
           print("-" * 90)
           for item in items:
               print(f"{item['ingredient']:<20} {item['lot_number']:<20} "
                     f"{item['quantity_on_hand']:<12.2f} {str(item['expiration_date']):<12} "
                     f"{item['days_until_expiry']}")
       else:
           print("\nNo ingredients expiring soon.")
  
   def report_batch_cost(self):
       print("\n----------- Batch Cost Summary -----------")
      
       query = """
           SELECT
               pb.lot_number,
               p.name AS product,
               pb.quantity_produced,
               pb.total_cost,
               pb.cost_per_unit,
               pb.production_date
           FROM Product_Batch pb
           JOIN Product p ON pb.product_id = p.product_id
           WHERE pb.manufacturer_id = %s
           ORDER BY pb.production_date DESC
       """
       self.cursor.execute(query, (self.current_user,))
       batches = self.cursor.fetchall()
      
       if batches:
           print(f"\n{'Lot Number':<20} {'Product':<20} {'Qty':<8} {'Total Cost':<12} {'Per Unit':<12} {'Date'}")
           print("-" * 95)
           for batch in batches:
               print(f"{batch['lot_number']:<20} {batch['product']:<20} "
                     f"{batch['quantity_produced']:<8} ${batch['total_cost']:<11.2f} "
                     f"${batch['cost_per_unit']:<11.4f} {batch['production_date']}")
       else:
           print("\nNo production batches found.")
  
  # supplier menu and functionality 
   def supplier_menu(self):
       while True:
           print("\nSUPPLIER MENU")
           print("---------------------------------------------------------------------------------------\n")
           print("  [1] Manage Ingredients Supplied")
           print("  [2] Define/Update Formulations")
           print("  [3] Create Ingredient Batch")
           print("  [0] Logout")
          
           choice = input("\nEnter choice: ").strip()
          
           if choice == '1':
               self.manage_ingredients_supplied()
           elif choice == '2':
               self.define_update_formulations()
           elif choice == '3':
               self.supplier_create_ingredient_batch()
           elif choice == '0':
               break
           else:
               print("Invalid choice. Please try again.")
  
   def manage_ingredients_supplied(self):
       print("\n----------- Manage Ingredients Supplied -----------")
      
       query = """
           SELECT i.ingredient_id, i.name, i.type
           FROM SUPPLIES s
           JOIN Ingredient i ON s.ingredient_id = i.ingredient_id
           WHERE s.supplier_id = %s
       """
       self.cursor.execute(query, (self.current_user,))
       supplied = self.cursor.fetchall()
      
       print("\nCurrently Supplied Ingredients:")
       if supplied:
           for ing in supplied:
               print(f"  [{ing['ingredient_id']}] {ing['name']} ({ing['type']})")
       else:
           print("  None")
      
       print("\n  [1] Add Ingredient")
       print("  [2] Remove Ingredient")
       print("  [0] Back")
      
       choice = input("\nEnter choice: ").strip()
      
       if choice == '1':
           self.add_ingredient_supply()
       elif choice == '2':
           self.remove_ingredient_supply()
  
   def add_ingredient_supply(self):
       self.cursor.execute("SELECT ingredient_id, name, type FROM Ingredient ORDER BY name")
       ingredients = self.cursor.fetchall()
      
       print("\nAll Ingredients:")
       for ing in ingredients:
           print(f"  [{ing['ingredient_id']}] {ing['name']} ({ing['type']})")
      
       try:
           ingredient_id = int(input("\nEnter Ingredient ID to add: ").strip())
          
           query = "INSERT INTO SUPPLIES (supplier_id, ingredient_id) VALUES (%s, %s)"
           self.cursor.execute(query, (self.current_user, ingredient_id))
           self.connection.commit()
          
           print("Ingredient added to your portfolio!")
          
       except Error as e:
           print(f"\nError: {e}")
           self.connection.rollback()
  
   def remove_ingredient_supply(self):
       try:
           ingredient_id = int(input("\nEnter Ingredient ID to remove: ").strip())
          
           query = "DELETE FROM SUPPLIES WHERE supplier_id = %s AND ingredient_id = %s"
           self.cursor.execute(query, (self.current_user, ingredient_id))
           self.connection.commit()
          
           if self.cursor.rowcount > 0:
               print("Ingredient removed from your portfolio!")
           else:
               print("Ingredient not found in your portfolio.")
              
       except Error as e:
           print(f"\nError: {e}")
           self.connection.rollback()
  
   def define_update_formulations(self):
       print("\n----------- Define/Update Formulations -----------")
      
       query = """
           SELECT i.ingredient_id, i.name, i.type
           FROM SUPPLIES s
           JOIN Ingredient i ON s.ingredient_id = i.ingredient_id
           WHERE s.supplier_id = %s AND i.type = 'compound'
       """
       self.cursor.execute(query, (self.current_user,))
       compounds = self.cursor.fetchall()
      
       if not compounds:
           print("\nYou don't supply any compound ingredients.")
           print("Only compound ingredients can have formulations.")
           return
      
       print("\nYour Compound Ingredients:")
       for ing in compounds:
           print(f"  [{ing['ingredient_id']}] {ing['name']}")
      
       try:
           ingredient_id_input = input("\nEnter Ingredient ID for formulation: ").strip()
           if not ingredient_id_input:
               print("Ingredient ID cannot be empty.")
               return
           ingredient_id = int(ingredient_id_input)
          
           # next version
           query = """
               SELECT MAX(version) as max_ver
               FROM Formulation
               WHERE supplier_id = %s AND ingredient_id = %s
           """
           self.cursor.execute(query, (self.current_user, ingredient_id))
           result = self.cursor.fetchone()
           new_version = (result['max_ver'] or 0) + 1
          
           print(f"\nCreating Formulation Version {new_version}")
          
           pack_size_input = input("Pack Size (oz): ").strip()
           if not pack_size_input:
               print("Pack size cannot be empty.")
               return
           pack_size = float(pack_size_input)
          
           unit_price_input = input("Unit Price ($): ").strip()
           if not unit_price_input:
               print("Unit price cannot be empty.")
               return
           unit_price = float(unit_price_input)
          
           start_date = input("Effective Start Date (YYYY-MM-DD): ").strip()
           if not start_date:
               print("Start date cannot be empty.")
               return
              
           end_date = input("Effective End Date (YYYY-MM-DD): ").strip()
           if not end_date:
               print("End date cannot be empty.")
               return
          
           query = """
               INSERT INTO Formulation
               (supplier_id, ingredient_id, version, pack_size, unit_price,
                effective_date_start, effective_date_end, is_active)
               VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
           """
           self.cursor.execute(query, (self.current_user, ingredient_id, new_version,
                                      pack_size, unit_price, start_date, end_date))
           formulation_id = self.cursor.lastrowid
          
           print("\nFormulation created!")
           print("\nNow add materials (atomic ingredients only)...")
          
           self.add_formulation_materials(formulation_id)
          
           self.connection.commit()
           print("\nFormulation defined successfully!")
          
       except Error as e:
           print(f"\nError: {e}")
           self.connection.rollback()
  
   def add_formulation_materials(self, formulation_id):

       self.cursor.execute("""
           SELECT ingredient_id, name
           FROM Ingredient
           WHERE type = 'atomic'
           ORDER BY name
       """)
       atomics = self.cursor.fetchall()
      
       print("\nAtomic Ingredients (materials):")
       for ing in atomics:
           print(f"  [{ing['ingredient_id']}] {ing['name']}")
      
       while True:
           try:
               print("\nAdd material (or 'done' to finish):")
               mat_input = input("Material Ingredient ID: ").strip()
              
               if mat_input.lower() == 'done':
                   break
              
               material_id = int(mat_input)
               quantity = float(input("Quantity (oz): ").strip())
              
               query = """
                   INSERT INTO CONTAINS_MATERIALS
                   (formulation_id, material_ingredient_id, quantity, unit_of_measure)
                   VALUES (%s, %s, %s, 'oz')
               """
               self.cursor.execute(query, (formulation_id, material_id, quantity))
               print("Material added to formulation")
              
           except ValueError:
               print("Invalid input.")
           except Error as e:
               print(f"Error: {e}")
  
   def supplier_create_ingredient_batch(self):
       print("\n----------- Create Ingredient Batch -----------")
      
       query = """
           SELECT i.ingredient_id, i.name, i.type
           FROM SUPPLIES s
           JOIN Ingredient i ON s.ingredient_id = i.ingredient_id
           WHERE s.supplier_id = %s
       """
       self.cursor.execute(query, (self.current_user,))
       supplied = self.cursor.fetchall()
      
       print("\nYour Ingredients:")
       for ing in supplied:
           print(f"  [{ing['ingredient_id']}] {ing['name']} ({ing['type']})")
      
       try:
           ingredient_id = int(input("\nIngredient ID: ").strip())
           batch_id = input("Batch ID (e.g., B0001): ").strip()
           quantity = float(input("Quantity (oz): ").strip())
           cost_per_unit = float(input("Cost per unit (oz): ").strip())
           expiration_str = input("Expiration Date (YYYY-MM-DD): ").strip()
          
           # make sure expiration is valid
           expiration_date = datetime.strptime(expiration_str, "%Y-%m-%d").date()
           min_expiration = datetime.now().date() + timedelta(days=90)
          
           if expiration_date < min_expiration:
               print(f"\nExpiration must be at least 90 days from today ({min_expiration})")
               return
          
           # for supplier creating batches we need a manufacturer id
           print("\nNote: Batch will be created for intake by manufacturer.")
           print("This is a simplified flow for demo purposes.")
          
           print("\nBatch validated. In production system, manufacturer would complete intake.")
          
       except ValueError:
           print("\nInvalid input format.")
       except Error as e:
           print(f"\nError: {e}")
  
#  viewer menu and functionality
   def viewer_menu(self):
       while True:
           print("\nVIEWER MENU (Read-Only)")
           print("---------------------------------------------------------------------------------------\n")
           print("  [1] Browse Products")
           print("  [2] Generate Product Ingredient List")
           print("  [3] Run Required Queries")
           print("  [0] Logout")
          
           choice = input("\nEnter choice: ").strip()
          
           if choice == '1':
               self.browse_products()
           elif choice == '2':
               self.generate_ingredient_list()
           elif choice == '3':
               self.run_required_queries()
           elif choice == '0':
               break
           else:
               print("Invalid choice. Please try again.")
  
   def browse_products(self):
       print("\n----------- Browse Products -----------")
      
       query = """
           SELECT
               p.product_id,
               p.name AS product_name,
               c.name AS category,
               m.name AS manufacturer,
               p.standard_batch_size
           FROM Product p
           JOIN Category c ON p.category_id = c.category_id
           JOIN Manufacturer m ON p.manufacturer_id = m.manufacturer_id
           ORDER BY c.name, m.name, p.name
       """
       self.cursor.execute(query)
       products = self.cursor.fetchall()
      
       if products:
           print(f"\n{'ID':<6} {'Product':<25} {'Category':<15} {'Manufacturer':<20} {'Batch Size'}")
           print("-" * 95)
           for p in products:
               print(f"{p['product_id']:<6} {p['product_name']:<25} {p['category']:<15} "
                     f"{p['manufacturer']:<20} {p['standard_batch_size']}")
       else:
           print("\nNo products found.")
  
   def generate_ingredient_list(self):
       print("\n----------- Generate Product Ingredient List -----------")
      
       self.browse_products()
      
       try:
           product_id = int(input("\nEnter Product ID: ").strip())
          
           query = """
               SELECT
                   final_ingredient_name AS ingredient,
                   SUM(final_quantity_per_unit) AS total_quantity,
                   unit_of_measure
               FROM v_FlattenedProductBOM
               WHERE product_id = %s
               GROUP BY final_ingredient_id, final_ingredient_name, unit_of_measure
               ORDER BY total_quantity DESC
           """
           self.cursor.execute(query, (product_id,))
           ingredients = self.cursor.fetchall()
          
           if ingredients:
               self.cursor.execute("SELECT name FROM Product WHERE product_id = %s", (product_id,))
               product = self.cursor.fetchone()
              
               print(f"\n----------- Ingredient List for {product['name']} -----------")
               print(f"{'Ingredient':<25} {'Quantity per Unit':<20} {'Unit'}")
               print("-" * 60)
               for ing in ingredients:
                   print(f"{ing['ingredient']:<25} {ing['total_quantity']:<20.4f} {ing['unit_of_measure']}")
           else:
               print("\nNo ingredients found or no active recipe for this product.")
              
       except ValueError:
           print("\nInvalid product ID.")
       except Error as e:
           print(f"\nError: {e}")
  
#   required queries for project
   def run_required_queries(self):
       while True:
           print("\nREQUIRED QUERIES")
           print("---------------------------------------------------------------------------------------\n")
           print("  [1] List all products and their categories")
           print("  [2] List ingredients for last batch of Steak Dinner (100) by MFG001")
           print("  [3] For MFG002, list suppliers and total spent with each")
           print("  [4] Which manufacturers has Supplier B (21) NOT supplied to?")
           print("  [5] Find unit cost for product lot 100-MFG001-B0901")
           print("  [0] Back")
          
           choice = input("\nEnter choice: ").strip()
          
           if choice == '1':
               self.query_1_products_categories()
           elif choice == '2':
               self.query_2_steak_dinner_ingredients()
           elif choice == '3':
               self.query_3_mfg002_suppliers()
           elif choice == '4':
               self.query_4_supplier_b_not_supplied()
           elif choice == '5':
               self.query_5_product_unit_cost()
           elif choice == '0':
               break
           else:
               print("Invalid choice.")
  
   def query_1_products_categories(self):
       print("\n----------- Query 1: All Products and Categories -----------")
      
       query = """
           SELECT
               p.product_id,
               p.name AS product_name,
               c.name AS category_name,
               m.name AS manufacturer
           FROM Product p
           JOIN Category c ON p.category_id = c.category_id
           JOIN Manufacturer m ON p.manufacturer_id = m.manufacturer_id
           ORDER BY c.name, p.name
       """
       self.cursor.execute(query)
       results = self.cursor.fetchall()
      
       if results:
           print(f"\n{'Product ID':<12} {'Product Name':<25} {'Category':<15} {'Manufacturer'}")
           print("-" * 80)
           for row in results:
               print(f"{row['product_id']:<12} {row['product_name']:<25} "
                     f"{row['category_name']:<15} {row['manufacturer']}")
       else:
           print("\nNo products found.")
  
   def query_2_steak_dinner_ingredients(self):
       print("\n----------- Query 2: Last Steak Dinner Batch Ingredients -----------")
      
       query = """
           SELECT
               i.name AS ingredient_name,
               c.ingredient_batch_lot_number AS lot_number,
               c.quantity_consumed
           FROM Product_Batch pb
           JOIN CONSUMES c ON pb.lot_number = c.product_batch_lot_number
           JOIN Ingredient_Batch ib ON c.ingredient_batch_lot_number = ib.lot_number
           JOIN Ingredient i ON ib.ingredient_id = i.ingredient_id
           WHERE pb.product_id = 100
             AND pb.manufacturer_id = 1
           ORDER BY pb.production_date DESC, i.name
           LIMIT 10
       """
       self.cursor.execute(query)
       results = self.cursor.fetchall()
      
       if results:
           print(f"\n{'Ingredient':<25} {'Lot Number':<25} {'Quantity Consumed'}")
           print("-" * 80)
           for row in results:
               print(f"{row['ingredient_name']:<25} {row['lot_number']:<25} "
                     f"{row['quantity_consumed']:.2f} oz")
       else:
           print("\nNo batches found.")
  
   def query_3_mfg002_suppliers(self):
       print("\n----------- Query 3: MFG002 Supplier Spending -----------")
      
       query = """
           SELECT
               s.name AS supplier_name,
               s.supplier_id,
               SUM(c.quantity_consumed * ib.cost_per_unit) AS total_spent
           FROM Product_Batch pb
           JOIN CONSUMES c ON pb.lot_number = c.product_batch_lot_number
           JOIN Ingredient_Batch ib ON c.ingredient_batch_lot_number = ib.lot_number
           JOIN Supplier s ON ib.supplier_id = s.supplier_id
           WHERE pb.manufacturer_id = 2
           GROUP BY s.supplier_id, s.name
           ORDER BY total_spent DESC
       """
       self.cursor.execute(query)
       results = self.cursor.fetchall()
      
       if results:
           print(f"\n{'Supplier ID':<15} {'Supplier Name':<20} {'Total Spent'}")
           print("-" * 60)
           for row in results:
               print(f"{row['supplier_id']:<15} {row['supplier_name']:<20} "
                     f"${row['total_spent']:.2f}")
       else:
           print("\nNo supplier transactions found for MFG002.")
  
   def query_4_supplier_b_not_supplied(self):
       print("\n----------- Query 4: Manufacturers NOT Supplied by Supplier B -----------")
      
       query = """
           SELECT
               m.manufacturer_id,
               m.name AS manufacturer_name
           FROM Manufacturer m
           WHERE m.manufacturer_id NOT IN (
               SELECT DISTINCT pb.manufacturer_id
               FROM Product_Batch pb
               JOIN CONSUMES c ON pb.lot_number = c.product_batch_lot_number
               JOIN Ingredient_Batch ib ON c.ingredient_batch_lot_number = ib.lot_number
               WHERE ib.supplier_id = 21
           )
           ORDER BY m.name
       """
       self.cursor.execute(query)
       results = self.cursor.fetchall()
      
       if results:
           print(f"\n{'Manufacturer ID':<20} {'Manufacturer Name'}")
           print("-" * 50)
           for row in results:
               print(f"{row['manufacturer_id']:<20} {row['manufacturer_name']}")
       else:
           print("\nSupplier B (21) has supplied to all manufacturers.")
  
   def query_5_product_unit_cost(self):
       print("\n----------- Query 5: Product Lot Unit Cost -----------")
      
       lot_number = input("Enter product lot number [100-MFG001-B0901]: ").strip() or "100-1-B0901"
      
       query = """
           SELECT
               pb.lot_number,
               p.name AS product_name,
               pb.quantity_produced,
               pb.total_cost,
               pb.cost_per_unit
           FROM Product_Batch pb
           JOIN Product p ON pb.product_id = p.product_id
           WHERE pb.lot_number = %s
       """
       self.cursor.execute(query, (lot_number,))
       result = self.cursor.fetchone()
      
       if result:
           print(f"\n{'Lot Number:':<20} {result['lot_number']}")
           print(f"{'Product:':<20} {result['product_name']}")
           print(f"{'Quantity Produced:':<20} {result['quantity_produced']} units")
           print(f"{'Total Cost:':<20} ${result['total_cost']:.2f}")
           print(f"{'Cost Per Unit:':<20} ${result['cost_per_unit']:.4f}")
       else:
           print(f"\nProduct lot '{lot_number}' not found.")
  
#   loops through application when runnning
   def run(self):
       print("\nINVENTORY MANAGEMENT SYSTEM")
       print("CSC440 Project 1")
       print("---------------------------------------------------------------------------------------\n")
      
       if not self.connect_to_database():
           print("\nFailed to connect to database, Exiting.")
           return
      
       try:
           while True:
               if not self.login():
                   break
       except KeyboardInterrupt:
           print("\n\nInterrupted by user.")
       finally:
           self.close_connection()
           print("\nSee you later!")




# actually runs the program


def main():
   app = InventoryManagementSystem()
   app.run()


if __name__ == "__main__":
   main()

