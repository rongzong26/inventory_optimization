# Migration Quick Start

## 🎯 Target Workspace Configuration

**Workspace URL:** https://adb-984752964297111.11.azuredatabricks.net  
**Profile:** `DEFAULT`  
**Catalog:** `rz_demo`  
**Schema:** `supply_chain`  
**Table:** `rz_demo.supply_chain.gold_master_part_inventory`

---

## ✅ Configuration Updated

The following files have been updated for the target workspace:

### 1. `inventory_optimization_bundle/databricks.yml`
- ✅ Workspace host updated to Azure workspace
- ⏳ SQL Warehouse ID (will be auto-filled by migration script)

### 2. `inventory_optimization_bundle/app/app.py`
- ✅ Table name updated to `rz_demo.supply_chain.gold_master_part_inventory`
- ⏳ Warehouse path (will be auto-filled by migration script)

### 3. `inventory_optimization_bundle/app/chat_assistant.py`
- ⏳ Genie Space ID (you need to create Genie space first)

---

## 🚀 Automated Migration (Recommended)

Run the automated migration script:

```bash
./migrate_to_target_workspace.sh
```

This script will:
1. ✅ Authenticate to target workspace
2. ✅ Find and configure SQL warehouse
3. ✅ Check if data exists (offer to migrate if not)
4. ✅ Guide you through Genie space setup
5. ✅ Deploy the app
6. ✅ Start the app
7. ✅ Provide next steps for permissions

---

## 📝 Manual Migration Steps

If you prefer manual control:

### Step 1: Authenticate

```bash
databricks auth login --profile DEFAULT
```

### Step 2: Verify Data in Target

Check if your table exists:

```bash
databricks sql-warehouse execute \
  --warehouse-id <YOUR_WAREHOUSE_ID> \
  --profile DEFAULT \
  --statement "SELECT COUNT(*) FROM rz_demo.supply_chain.gold_master_part_inventory"
```

### Step 3: Get SQL Warehouse ID

```bash
databricks warehouses list --profile DEFAULT
```

Copy the warehouse ID and update:
- `inventory_optimization_bundle/databricks.yml` (line ~14)
- `inventory_optimization_bundle/app/app.py` (line ~12)

### Step 4: Create Genie Space

1. Go to: https://adb-984752964297111.11.azuredatabricks.net/genie
2. Click "Create Space"
3. Name: "Inventory Optimization"
4. Add table: `rz_demo.supply_chain.gold_master_part_inventory`
5. Copy Space ID from URL
6. Update `inventory_optimization_bundle/app/chat_assistant.py` line 8

### Step 5: Deploy App

```bash
cd inventory_optimization_bundle

# Validate
databricks bundle validate --profile DEFAULT

# Deploy
databricks bundle deploy --profile DEFAULT

# Start
databricks bundle run inventory-optimization-app --profile DEFAULT
```

### Step 6: Configure Permissions

```bash
# Get service principal ID
databricks apps get inventory-optimization-app --profile DEFAULT

# Grant Genie access (in UI):
# Genie space → Share → Add the service principal with CAN_USE
```

---

## 🗺️ Migration Checklist

### Pre-Migration
- [ ] Authenticate: `databricks auth login --profile DEFAULT`
- [ ] Verify data exists in `rz_demo.supply_chain.gold_master_part_inventory`
- [ ] Have access to create apps in target workspace
- [ ] SQL Warehouse available and running

### Data Verification
```sql
-- Check table exists
SHOW TABLES IN rz_demo.supply_chain;

-- Check row count
SELECT COUNT(*) FROM rz_demo.supply_chain.gold_master_part_inventory;

-- Check schema
DESCRIBE TABLE rz_demo.supply_chain.gold_master_part_inventory;

-- Sample data
SELECT * FROM rz_demo.supply_chain.gold_master_part_inventory LIMIT 10;
```

### Genie Setup
- [ ] Create Genie space in target workspace
- [ ] Add `rz_demo.supply_chain.gold_master_part_inventory` table
- [ ] Test queries: "How many parts are in inventory?"
- [ ] Copy Space ID from URL
- [ ] Update `chat_assistant.py` with Space ID

### Deployment
- [ ] SQL Warehouse ID updated in `databricks.yml`
- [ ] Bundle validated: `databricks bundle validate --profile DEFAULT`
- [ ] Bundle deployed: `databricks bundle deploy --profile DEFAULT`
- [ ] App started: `databricks bundle run inventory-optimization-app --profile DEFAULT`

### Post-Deployment
- [ ] Get app URL: `databricks apps get inventory-optimization-app --profile DEFAULT`
- [ ] Get service principal ID from app details
- [ ] Grant Genie permissions to service principal
- [ ] Test app: Visit URL and verify all features work
- [ ] Check logs if issues: `databricks apps logs inventory-optimization-app --profile DEFAULT`

---

## 🔍 Verification Commands

### Check App Status
```bash
databricks apps get inventory-optimization-app --profile DEFAULT
```

### View App Logs
```bash
databricks apps logs inventory-optimization-app --profile DEFAULT
```

### Check SQL Warehouse
```bash
databricks warehouses list --profile DEFAULT
```

### Test Data Access
```bash
databricks sql-warehouse execute \
  --warehouse-id <WAREHOUSE_ID> \
  --profile DEFAULT \
  --statement "SELECT plant_name, COUNT(*) as part_count 
               FROM rz_demo.supply_chain.gold_master_part_inventory 
               GROUP BY plant_name"
```

---

## 🐛 Common Issues

### Issue: "Table not found"
**Solution:** Verify table name matches exactly `rz_demo.supply_chain.gold_master_part_inventory`

### Issue: Genie queries fail
**Solution:** 
1. Check Genie space has table added
2. Grant service principal `CAN_USE` on Genie space
3. Verify Space ID in `chat_assistant.py`

### Issue: App won't start
**Solution:**
1. Check logs: `databricks apps logs inventory-optimization-app --profile DEFAULT`
2. Verify SQL warehouse is running
3. Check bundle validation passed

### Issue: "Permission denied" errors
**Solution:**
1. Verify service principal has `SELECT` on table
2. Grant Genie space access
3. Check SQL warehouse permissions

---

## 📊 Expected Results

After successful migration:
- ✅ App accessible at: `https://<app-id>.azuredatabricksapps.net`
- ✅ Map displays inventory across sites
- ✅ Data grid shows all inventory records
- ✅ Inventory Assistant responds to queries
- ✅ AI recommendations work
- ✅ All KPIs display correctly

---

## 🔄 Rollback

If you need to rollback to the previous workspace:

```bash
# Stop app in target
databricks apps stop inventory-optimization-app --profile DEFAULT

# Delete app (optional)
databricks apps delete inventory-optimization-app --profile DEFAULT

# App in source workspace (fe-sandbox-serverless) remains unchanged
```

---

## 📞 Need Help?

1. **Check migration guide:** `WORKSPACE_MIGRATION_GUIDE.md`
2. **View logs:** `databricks apps logs inventory-optimization-app --profile DEFAULT`
3. **Test connection:** Verify you can query the table manually
4. **Genie issues:** Test Genie space independently before app integration

---

**Created:** January 30, 2026  
**Target:** Azure Databricks (adb-984752964297111.11.azuredatabricks.net)  
**Catalog/Schema:** rz_demo.supply_chain
