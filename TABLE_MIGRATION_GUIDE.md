# Table Migration Guide
## Inventory Optimization Data Migration

This guide explains how to migrate tables from the source workspace (`supply-chain`) to the target workspace (`fe-sandbox-serverless`).

---

## 📊 Tables to Migrate

### Raw Tables (8 tables):
1. `raw_plants` - Mine site locations and coordinates
2. `raw_parts` - Part catalog and descriptions
3. `raw_equipment` - Equipment inventory
4. `raw_vendors` - Vendor information
5. `raw_vendor_parts` - Vendor-part relationships
6. `raw_parts_inventory` - Current inventory levels
7. `raw_inventory_reservations` - Reserved parts
8. `raw_planned_maintenance` - Planned maintenance schedules

### Gold Table (1 table):
- `gold_master_part_inventory` - Aggregated inventory view with risk calculations

---

## 🔄 Migration Methods

###Option 1: In-Workspace Notebook Migration (RECOMMENDED)

Since both workspaces are separate, we need to:
1. Export data from SOURCE workspace
2. Transfer to TARGET workspace
3. Create gold table in TARGET

#### Step 1: Run Export Notebook in SOURCE Workspace

1. **Upload to SOURCE workspace** (`supply-chain`):
   ```bash
   databricks workspace import /Users/rong.zong@databricks.com/Export_Tables \
     --file ./Export_Tables_Notebook.py \
     --language PYTHON \
     --format SOURCE \
     --profile supply-chain
   ```

2. **Open and Run** the notebook in the source workspace
   - It will export all tables to Delta format in a temporary location

#### Step 2: Run Import Notebook in TARGET Workspace

1. **Upload to TARGET workspace** (`fe-sandbox-serverless`):
   ```bash
   databricks workspace import /Users/rong.zong@databricks.com/Import_Tables \
     --file ./Import_Tables_Notebook.py \
     --language PYTHON \
     --format SOURCE \
     --profile fe-sandbox-serverless
   ```

2. **Open and Run** the notebook
   - Reads exported data
   - Creates tables in `main.inventory_optimization`
   - Generates gold table

---

### Option 2: Manual Table Creation with Sample Data

If you prefer to start fresh with sample data for testing:

1. Run the notebook `Create_Sample_Data.py` in the TARGET workspace
2. It will create all tables with realistic sample data
3. The app will work immediately for demonstration purposes

---

## 📋 Verification Steps

After migration, verify in the TARGET workspace:

```sql
-- Check all tables exist
SHOW TABLES IN main.inventory_optimization;

-- Verify row counts
SELECT 'raw_plants' as table_name, COUNT(*) as row_count FROM main.inventory_optimization.raw_plants
UNION ALL
SELECT 'raw_parts', COUNT(*) FROM main.inventory_optimization.raw_parts
UNION ALL  
SELECT 'raw_equipment', COUNT(*) FROM main.inventory_optimization.raw_equipment
UNION ALL
SELECT 'raw_vendors', COUNT(*) FROM main.inventory_optimization.raw_vendors
UNION ALL
SELECT 'raw_vendor_parts', COUNT(*) FROM main.inventory_optimization.raw_vendor_parts
UNION ALL
SELECT 'raw_parts_inventory', COUNT(*) FROM main.inventory_optimization.raw_parts_inventory
UNION ALL
SELECT 'raw_inventory_reservations', COUNT(*) FROM main.inventory_optimization.raw_inventory_reservations
UNION ALL
SELECT 'raw_planned_maintenance', COUNT(*) FROM main.inventory_optimization.raw_planned_maintenance
UNION ALL
SELECT 'gold_master_part_inventory', COUNT(*) FROM main.inventory_optimization.gold_master_part_inventory;
```

---

## 🔧 Update App Configuration

After tables are migrated, update the app to use the new location:

1. Navigate to: `inventory_optimization_bundle/app/app.py`
2. Update line 12:
   ```python
   # OLD:
   TABLE_NAME = os.getenv("DATABRICKS_TABLE_NAME", "users.david_hurley.gold_master_part_inventory")
   
   # NEW:
   TABLE_NAME = os.getenv("DATABRICKS_TABLE_NAME", "main.inventory_optimization.gold_master_part_inventory")
   ```

3. Redeploy the bundle:
   ```bash
   cd inventory_optimization_bundle
   databricks bundle deploy --profile fe-sandbox-serverless
   ```

4. Restart the app:
   ```bash
   databricks apps start inventory-optimization-app --profile fe-sandbox-serverless
   ```

---

## 📁 Files Included

- `Table_Migration_Notebook.py` - Complete migration notebook for same-workspace scenarios
- `Export_Tables_Notebook.py` - Export tables from SOURCE workspace
- `Import_Tables_Notebook.py` - Import tables to TARGET workspace  
- `Create_Sample_Data.py` - Generate sample data for testing
- `migrate_tables.py` - Python script for programmatic migration (requires databricks-sql-connector)

---

## ⚠️ Important Notes

1. **Workspace Isolation**: The two workspaces (`supply-chain` and `fe-sandbox-serverless`) are separate environments. Data cannot be queried across them directly.

2. **Catalog Differences**: 
   - SOURCE has `users` catalog
   - TARGET has `main` catalog (no `users` catalog)

3. **Schema Locations**:
   - SOURCE: `users.david_hurley.*`
   - TARGET: `main.inventory_optimization.*`

4. **Warehouse Requirements**: Ensure SQL warehouses are running before executing notebooks

5. **Permissions**: You need CREATE TABLE permissions in `main.inventory_optimization`

---

## 🚀 Quick Start (Recommended Path)

For fastest deployment with sample data:

```bash
# 1. Upload sample data notebook to target workspace
databricks workspace import /Users/rong.zong@databricks.com/Create_Sample_Data \
  --file ./Create_Sample_Data.py \
  --language PYTHON \
  --format SOURCE \
  --profile fe-sandbox-serverless

# 2. Run the notebook in the workspace UI

# 3. Update app configuration
cd inventory_optimization_bundle
# Edit app/app.py to change TABLE_NAME

# 4. Redeploy
databricks bundle deploy --profile fe-sandbox-serverless

# 5. Start app
databricks apps start inventory-optimization-app --profile fe-sandbox-serverless
```

Your app will be live with demo data in minutes!

---

## 📞 Support

If you encounter issues:
- Check SQL warehouse is running in target workspace
- Verify schema `main.inventory_optimization` exists
- Check app logs: `databricks apps logs inventory-optimization-app --profile fe-sandbox-serverless`
