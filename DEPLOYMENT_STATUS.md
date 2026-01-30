# Deployment Status - Target Workspace

**Target Workspace:** https://adb-984752964297111.11.azuredatabricks.net  
**Profile:** `DEFAULT`  
**Date:** January 30, 2026

---

## ✅ Configuration Complete

### App Configuration
- ✅ **Workspace URL** → `https://adb-984752964297111.11.azuredatabricks.net`
- ✅ **Catalog/Schema** → `rz_demo.supply_chain`
- ✅ **Table** → `rz_demo.supply_chain.gold_master_part_inventory`
- ✅ **Genie Space ID** → `01f0fe11faaf1757941b620cb450e408`

### Files Updated
- ✅ `databricks.yml` - Workspace host and Genie Space URL
- ✅ `app.py` - Table name with new catalog/schema
- ✅ `chat_assistant.py` - Genie Space ID configured

### Migration Tools Ready
- ✅ `migrate_to_target_workspace.sh` - Automated deployment
- ✅ `verify_target_setup.sh` - Pre-deployment verification

---

## ⏳ Pending: Warehouse ID

**Status:** Needs authentication to retrieve

The SQL Warehouse ID is currently set to `TBD_UPDATE_AFTER_AUTH` in:
- `databricks.yml` (line 14)
- `app.py` (line 12)

This will be automatically filled when you run the migration script.

---

## 🚀 Ready to Deploy!

### Option 1: Automated Deployment (Recommended)

Run the migration script which will:
1. Authenticate you
2. Find SQL warehouse automatically
3. Update all configs
4. Deploy and start the app

```bash
./migrate_to_target_workspace.sh
```

### Option 2: Manual Deployment

If you prefer step-by-step control:

#### Step 1: Authenticate
```bash
databricks auth login --profile DEFAULT
```

#### Step 2: Get SQL Warehouse ID
```bash
databricks warehouses list --profile DEFAULT --output json | jq -r '.[0].id'
```

#### Step 3: Update Configuration Files

**Update databricks.yml (line 14):**
```yaml
sql_warehouse:
  id: <YOUR_WAREHOUSE_ID>
  permission: "CAN_USE"
```

**Update app.py (line 12):**
```python
HTTP_PATH = os.getenv("DATABRICKS_WAREHOUSE_HTTP_PATH", "/sql/1.0/warehouses/<YOUR_WAREHOUSE_ID>")
```

#### Step 4: Deploy
```bash
cd inventory_optimization_bundle

# Validate
databricks bundle validate --profile DEFAULT

# Deploy
databricks bundle deploy --profile DEFAULT

# Start
databricks bundle run inventory-optimization-app --profile DEFAULT
```

#### Step 5: Get App Details
```bash
databricks apps get inventory-optimization-app --profile DEFAULT
```

Copy the:
- **App URL** - to access the app
- **Service Principal ID** - for Genie permissions

#### Step 6: Grant Genie Permissions

1. Go to: https://adb-984752964297111.11.azuredatabricks.net/genie/rooms/01f0fe11faaf1757941b620cb450e408
2. Click "Share" or permissions icon
3. Add the service principal ID
4. Grant "CAN_USE" permission
5. Save

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Authenticated to target workspace: `databricks auth login --profile DEFAULT`
- [ ] Data exists in `rz_demo.supply_chain.gold_master_part_inventory`
- [ ] SQL Warehouse exists and is running
- [ ] Genie Space created with table added
- [ ] Genie Space tested with sample queries

### During Deployment
- [ ] SQL Warehouse ID configured
- [ ] Bundle validated successfully
- [ ] App deployed without errors
- [ ] App started and status is RUNNING

### Post-Deployment
- [ ] App URL accessible
- [ ] Service Principal ID retrieved
- [ ] Genie permissions granted to service principal
- [ ] Map loads with inventory data
- [ ] Data grid displays records
- [ ] Inventory Assistant responds to queries
- [ ] AI recommendations work

---

## 🔗 Key URLs

### Workspace & App
- **Workspace:** https://adb-984752964297111.11.azuredatabricks.net
- **App URL:** (will be available after deployment)

### Genie Space
- **URL:** https://adb-984752964297111.11.azuredatabricks.net/genie/rooms/01f0fe11faaf1757941b620cb450e408
- **Space ID:** `01f0fe11faaf1757941b620cb450e408`
- **Table:** `rz_demo.supply_chain.gold_master_part_inventory`

### Data
- **Catalog:** `rz_demo`
- **Schema:** `supply_chain`
- **Table:** `gold_master_part_inventory`
- **Full Name:** `rz_demo.supply_chain.gold_master_part_inventory`

---

## 🧪 Test Your Genie Space First

Before deploying the app, verify your Genie space works:

1. Go to: https://adb-984752964297111.11.azuredatabricks.net/genie/rooms/01f0fe11faaf1757941b620cb450e408

2. Test these queries:
   ```
   How many parts are in the inventory?
   Which sites have low stock?
   What equipment has the most critical parts?
   Show me parts that need reordering
   ```

3. Verify:
   - ✅ SQL is generated correctly
   - ✅ Results are returned
   - ✅ Table `rz_demo.supply_chain.gold_master_part_inventory` is accessible

If Genie works standalone, it will work in the app (after permissions).

---

## 📊 Expected Deployment Time

| Step | Time | Notes |
|------|------|-------|
| Authentication | 1 min | First time only |
| Get Warehouse ID | 30 sec | Automated by script |
| Bundle Validation | 30 sec | Checks config |
| Bundle Deployment | 2-3 min | Uploads and configures |
| App Startup | 2-3 min | Provisions compute |
| Grant Permissions | 1 min | Manual UI step |
| **Total** | **~8 min** | With automated script |

---

## 🎯 After Deployment

### Verify App Works

1. **Access App URL** (from deployment output)

2. **Test Features:**
   - ✅ Map loads with site markers
   - ✅ Click markers to see inventory details
   - ✅ Data grid shows all inventory records
   - ✅ Search and filters work
   - ✅ Inventory Assistant opens (chat icon)
   - ✅ Ask a question in chat (e.g., "What parts are low stock?")
   - ✅ Select items and get AI recommendations

3. **Check Logs (if issues):**
   ```bash
   databricks apps logs inventory-optimization-app --profile DEFAULT
   ```

### Common Post-Deployment Issues

**Issue: Inventory Assistant returns errors**
- **Cause:** Service principal doesn't have Genie permissions
- **Fix:** Grant `CAN_USE` on Genie space to service principal

**Issue: No data shown in app**
- **Cause:** SQL warehouse not accessible or table permissions
- **Fix:** Verify table exists and warehouse is running

**Issue: Map doesn't load**
- **Cause:** Missing lat/lon columns or invalid data
- **Fix:** Verify table schema matches expected format

---

## 📝 Deployment Commands Quick Reference

```bash
# Authenticate
databricks auth login --profile DEFAULT

# Option A: Automated (Recommended)
./migrate_to_target_workspace.sh

# Option B: Manual
databricks warehouses list --profile DEFAULT
# Update configs with warehouse ID
cd inventory_optimization_bundle
databricks bundle validate --profile DEFAULT
databricks bundle deploy --profile DEFAULT
databricks bundle run inventory-optimization-app --profile DEFAULT

# Get app details
databricks apps get inventory-optimization-app --profile DEFAULT

# View logs
databricks apps logs inventory-optimization-app --profile DEFAULT

# Stop app (if needed)
databricks apps stop inventory-optimization-app --profile DEFAULT

# Restart app
databricks apps start inventory-optimization-app --profile DEFAULT
```

---

## 🎉 You're Ready!

All configuration is complete. Your app is ready to deploy to the target workspace.

**Next Step:** Run the deployment!

```bash
./migrate_to_target_workspace.sh
```

Or follow the manual steps above if you prefer step-by-step control.

---

**Configuration Status:** ✅ Complete  
**Genie Space:** ✅ Configured  
**Ready to Deploy:** ✅ Yes

**Run `./migrate_to_target_workspace.sh` to deploy now!**
