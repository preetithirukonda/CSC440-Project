# CSC440 Project - Product Formulation & Inventory Management System

## Team Members
- Preeti Thirukonda
- Shuhan Zhuang
- Dylan Wilkins
- Joshua Wilson

## Project Overview
This project implements a relational database system used to manage:
- Manufacturers
- Suppliers
- Ingredient inventory (atomic + compound)
- Products
- Formulations & recipes (with versioning rules)
- Product & ingredient batches
- Supplier relationships
- Business rules enforced via triggers and stored procedures

The database enforces realistic constraints such as non overlapping formulation dates, one active recipe per product, valid batch expiration rules, and consistent unit measures.

## Project Files
1. schema.sql
Contains:
- Table definitions
- Primary/foreign keys
- CHECK constraints
- Triggers
- Stored procedure definitions
- Relationship tables


This file must be executed first.

2. queries.sql 
- Contains valid sample INSERT statements for:
- Manufacturers
- Suppliers
- Categories
- Ingredients (atomic + compound)
- Products
- Recipes (with correct versioning)
- Formulations (non-overlapping effective dates)
- Ingredient batches
- Product batches
- SUPPLIED_BY, CONTAIN_MATERIALS, and REQUIRES tables

All data adheres to constraints defined in schema.sql.

3. /src/ — Source Code
Includes Python source code demonstrating:
- Database connection
- Executing stored procedures
- Running operations
- Retrieving reports

Executable:
main.py 

## Setup Instructions
Database Setup

1. Open SQL environment MySQL Workbench.


2. Run: schema.sql


3. After successful schema creation, run: queries.sql


Warning: running the data file before the schema file will cause constraint and trigger errors.

## Running the Source Code

```
pip3 install mysql-connector-python   
python3 main.py
```
The CLI will lead you through all project required functionality, following the flow outlined in Appendix A.

## Additional Notes

All sample records were tested to ensure no violations of triggers or constraints.
Only one active recipe exists per product at any time.
Formulation date ranges are valid and do not overlap.
Ingredient batches follow expiration and unit measure rules.
Product batches reference valid recipes and contain logical quantities.
Stored procedures assume schema and data are loaded first.
