# Workspace Migration Guide

Complete guide to migrate the Inventory Optimization App and all related resources to another Databricks workspace.

---

## 📋 Current Setup Overview

### Current Workspace
- **Host:** `https://fe-sandbox-serverless-v7m02q.cloud.databricks.com`
- **Profile:** `fe-sandbox-serverless`
- **App URL:** https://inventory-optimization-app-7474656208178943.aws.databricksapps.com

### Resources to Migrate

#### 1. **Databricks App**
- Bundle name: `inventory_optimization_buildathon`
- App name: `inventory-optimization-app`
- Source code: `inventory_optimization_bundle/app/`

#### 2. **Data Tables**
- Primary table: `rz-demo-mining.supply-chain.gold_master_part_inventory`
- Raw tables (if any): Check catalog `rz-demo-mining`, schema `supply-chain`

#### 3. **Genie Space**
- Space ID: `01f0fd5cc0c912fcbe49b206c5b467d6`
- Space URL: https://fe-sandbox-serverless-v7m02q.cloud.databricks.com/genie/rooms/01f0fd5cc0c912fcbe49b206c5b467d6
- Tables: `gold_master_part_inventory`

#### 4. **Infrastructure Resources**
- SQL Warehouse ID: `a2188971f887cd35` (Serverless Starter Warehouse)
- LLM Endpoint: `databricks-claude-sonnet-4-5`

#### 5. **Optional: Agent Framework** (if deployed)
- Model: `rz-demo-mining-supply-chain-inventory_genie_agent`
- Endpoint: Similar naming convention
- Secrets: `genie-agent/databricks-token`

---

## 🎯 Migration Checklist

### Pre-Migration
- [ ] Target workspace URL and access confirmed
- [ ] Databricks CLI profile for target workspace configured
- [ ] Permissions in target workspace (admin or app creator)
- [ ] SQL Warehouse available in target workspace
- [ ] Claude Sonnet endpoint access confirmed

### Data Migration
- [ ] Catalog and schema created in target workspace
- [ ] Data tables exported from source
- [ ] Data tables imported to target
- [ ] Table permissions configured

### Genie Migration
- [ ] Genie space created in target workspace
- [ ] Genie space configured with tables
- [ ] Genie space tested with queries

### App Migration
- [ ] Bundle configuration updated
- [ ] App deployed to target workspace
- [ ] App permissions configured
- [ ] App tested and verified

---

## 🚀 Step-by-Step Migration Process

### Step 1: Setup Target Workspace Profile

First, configure the Databricks CLI for your target workspace:

```bash
# Interactive configuration
databricks configure --profile <target-profile-name>

# You'll be prompted for:
# - Host: https://<target-workspace>.cloud.databricks.com
# - Token: <your-personal-access-token>
```

**Or manually edit** `~/.databrickscfg`:

```ini
[<target-profile-name>]
host = https://<target-workspace>.cloud.databricks.com
token = <your-pat>
```

### Step 2: Export Data Tables

#### Option A: Using Databricks CLI (Recommended for small-medium data)

```bash
# Export table to CSV
databricks sql-warehouse execute \
  --warehouse-id a2188971f887cd35 \
  --profile fe-sandbox-serverless \
  --query "SELECT * FROM \`rz-demo-mining\`.\`supply-chain\`.\`gold_master_part_inventory\`" \
  --format csv \
  > gold_master_part_inventory.csv
```

#### Option B: Using Delta Lake (Recommended for large data)

Create a notebook in the source workspace:

```python
# Export to DBFS
source_table = "`rz-demo-mining`.`supply-chain`.`gold_master_part_inventory`"
export_path = "/dbfs/tmp/inventory_migration/gold_master_part_inventory"

df = spark.table(source_table)
df.write.format("parquet").mode("overwrite").save(export_path)

# Download via CLI
# databricks fs cp -r dbfs:/tmp/inventory_migration/ ./inventory_migration/ --profile fe-sandbox-serverless
```

#### Option C: Using COPY INTO (Best for very large data)

```sql
-- In source workspace
COPY (SELECT * FROM `rz-demo-mining`.`supply-chain`.`gold_master_part_inventory`)
TO '/tmp/inventory_export/gold_master_part_inventory'
FILEFORMAT = PARQUET;
```

### Step 3: Create Target Catalog and Schema

In the **target workspace**, run:

```sql
-- Create catalog (or use existing)
CREATE CATALOG IF NOT EXISTS <target_catalog>;

-- Create schema
CREATE SCHEMA IF NOT EXISTS <target_catalog>.<target_schema>;

-- Grant permissions
GRANT USE CATALOG ON CATALOG <target_catalog> TO `account users`;
GRANT USE SCHEMA ON SCHEMA <target_catalog>.<target_schema> TO `account users`;
```

### Step 4: Import Data to Target

#### Using Parquet files:

```python
# In target workspace notebook
import_path = "/dbfs/tmp/inventory_migration/gold_master_part_inventory"
target_table = "`<target_catalog>`.`<target_schema>`.`gold_master_part_inventory`"

df = spark.read.format("parquet").load(import_path)
df.write.format("delta").mode("overwrite").saveAsTable(target_table)
```

#### Using CSV:

```python
# Upload CSV first via CLI:
# databricks fs cp gold_master_part_inventory.csv dbfs:/tmp/inventory_migration/ --profile <target-profile>

# Then in notebook:
df = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load("/tmp/inventory_migration/gold_master_part_inventory.csv")
df.write.format("delta").mode("overwrite").saveAsTable("`<target_catalog>`.`<target_schema>`.`gold_master_part_inventory`")
```

### Step 5: Create and Configure Genie Space

1. **Create Genie Space** in target workspace:
   - Navigate to: https://<target-workspace>/genie
   - Click "Create Space"
   - Name: "Inventory Optimization"
   - Description: "Supply chain inventory queries"

2. **Add Tables to Genie:**
   - In Genie space settings
   - Add table: `<target_catalog>.<target_schema>.gold_master_part_inventory`
   - Add descriptions for better AI understanding

3. **Test Genie Space:**
   - Ask: "How many parts are in the inventory?"
   - Ask: "What sites have low stock?"
   - Verify SQL generation and results

4. **Copy Genie Space ID:**
   - From URL: `https://<target-workspace>/genie/rooms/<SPACE_ID>`
   - You'll need this for app configuration

### Step 6: Verify Target Infrastructure

Check required resources exist:

```bash
# List SQL warehouses
databricks sql-warehouses list --profile <target-profile>

# Check Claude endpoint (if available)
databricks serving-endpoints get databricks-claude-sonnet-4-5 --profile <target-profile>
```

**Note the SQL Warehouse ID** - you'll need it for the app configuration.

### Step 7: Update App Configuration

Edit `inventory_optimization_bundle/databricks.yml`:

```yaml
bundle:
  name: inventory_optimization_buildathon

resources:
  apps:
    inventory-optimization-app:
      name: 'inventory-optimization-app'
      source_code_path: ./app
      description: "An inventory optimization app that uses a SQL warehouse and Genie"
      resources:
        - name: "sql-warehouse"
          description: "A SQL warehouse for app to be able to work with"
          sql_warehouse:
            id: <TARGET_WAREHOUSE_ID>  # ← UPDATE THIS
            permission: "CAN_USE"
        - name: "serving-endpoint"
          description: "A serving endpoint for the app to use"
          serving_endpoint:
            name: databricks-claude-sonnet-4-5
            permission: "CAN_QUERY"
        # NOTE: Update Genie Space ID in chat_assistant.py
        # Genie Space ID: <NEW_GENIE_SPACE_ID>  # ← UPDATE THIS

targets:
  dev:
    mode: development
    default: true
    workspace:
      host: https://<target-workspace>.cloud.databricks.com  # ← UPDATE THIS
```

Edit `inventory_optimization_bundle/app/chat_assistant.py`:

```python
# Update line 8:
GENIE_SPACE_ID = "<NEW_GENIE_SPACE_ID>"  # ← UPDATE THIS
```

Edit `inventory_optimization_bundle/app/app.py`:

```python
# Update line ~30-35:
TABLE_NAME = "`<target_catalog>`.`<target_schema>`.`gold_master_part_inventory`"  # ← UPDATE THIS
```

### Step 8: Deploy App to Target Workspace

```bash
cd inventory_optimization_bundle

# Validate configuration
databricks bundle validate --profile <target-profile>

# Deploy
databricks bundle deploy --profile <target-profile>

# Start the app
databricks bundle run inventory-optimization-app --profile <target-profile>
```

### Step 9: Configure App Permissions

The app's service principal needs Genie space access:

1. **Find the service principal:**
   ```bash
   databricks apps get inventory-optimization-app --profile <target-profile>
   # Look for: service_principal_id
   ```

2. **Grant Genie permissions:**
   - Go to Genie space: https://<target-workspace>/genie/rooms/<SPACE_ID>
   - Click "Share" or "Permissions"
   - Add the service principal ID with "CAN_USE" permission

3. **Or use the script:**
   ```bash
   # Update scripts/grant_genie_permissions.sh with new IDs
   ./inventory_optimization_bundle/scripts/grant_genie_permissions.sh
   ```

### Step 10: Verify Migration

1. **Check app status:**
   ```bash
   databricks apps get inventory-optimization-app --profile <target-profile>
   ```

2. **Access app URL** (from output above)

3. **Test features:**
   - ✅ Map loads with inventory data
   - ✅ Data grid shows all records
   - ✅ Inventory Assistant responds to queries
   - ✅ AI recommendations work
   - ✅ All KPIs display correctly

4. **Check logs if issues:**
   ```bash
   databricks apps logs inventory-optimization-app --profile <target-profile>
   ```

---

## 🔄 Optional: Migrate Agent Framework

If you deployed the Genie Agent (Model Serving endpoint):

### 1. Export Agent Model

```bash
# From source workspace
# The agent code is already in: inventory_optimization_bundle/agent/

# If you need the registered model:
# It's in Unity Catalog: rz-demo-mining.supply-chain.inventory_genie_agent
```

### 2. Create Secrets in Target

```bash
# Create secret scope
databricks secrets create-scope genie-agent --profile <target-profile>

# Create PAT and store it
databricks secrets put-secret genie-agent databricks-token --profile <target-profile>
# Paste your PAT when prompted
```

### 3. Deploy Agent in Target

Use the `Deploy_Genie_Agent.py` notebook in the target workspace:

1. Import notebook to target workspace
2. Update catalog/schema names
3. Update Genie space ID
4. Run the notebook

---

## 📊 Migration Summary Template

After migration, document what was moved:

```markdown
## Migration Summary

**Date:** [DATE]
**From:** fe-sandbox-serverless-v7m02q
**To:** [TARGET_WORKSPACE]

### Resources Migrated:
- ✅ Data tables: [X] tables, [Y] GB
- ✅ Genie space: [SPACE_ID]
- ✅ Databricks App: [APP_URL]
- ⬜ Agent Framework: [Yes/No]

### Configuration Updates:
- Catalog: [OLD] → [NEW]
- Schema: [OLD] → [NEW]
- SQL Warehouse: [OLD_ID] → [NEW_ID]
- Genie Space: [OLD_ID] → [NEW_ID]

### Issues Encountered:
[List any issues and resolutions]

### Verification:
- ✅ App accessible
- ✅ Data loading correctly
- ✅ Genie queries working
- ✅ AI recommendations working
```

---

## 🐛 Troubleshooting

### Issue: App Can't Access Data

**Symptoms:** Empty tables, permission errors in logs

**Solutions:**
1. Check table exists: `SHOW TABLES IN <catalog>.<schema>`
2. Grant permissions:
   ```sql
   GRANT SELECT ON TABLE <catalog>.<schema>.<table> TO `account users`;
   ```
3. Verify app service principal has access

### Issue: Genie Queries Failing

**Symptoms:** "PERMISSION_DENIED" errors, "Failed to fetch tables"

**Solutions:**
1. Verify Genie space has tables added
2. Grant app service principal `CAN_USE` on Genie space
3. Verify tables are accessible in Genie space settings

### Issue: LLM Endpoint Not Available

**Symptoms:** "Endpoint not found" errors

**Solutions:**
1. Check endpoint exists: `databricks serving-endpoints get databricks-claude-sonnet-4-5`
2. Use different endpoint name if needed
3. Request access to Claude endpoints in target workspace

### Issue: SQL Warehouse Not Accessible

**Symptoms:** Connection timeout, permission errors

**Solutions:**
1. Verify warehouse is running
2. Grant `CAN_USE` permission
3. Update warehouse ID in databricks.yml

---

## 🔒 Security Considerations

1. **Credentials:**
   - Don't commit PATs or tokens to Git
   - Use Databricks Secrets for sensitive data
   - Rotate tokens after migration

2. **Permissions:**
   - Follow principle of least privilege
   - Use service principals for apps
   - Audit access after migration

3. **Data:**
   - Verify data encryption in transit
   - Check Unity Catalog governance policies
   - Review table ACLs

---

## ✅ Post-Migration Tasks

- [ ] Update documentation with new URLs
- [ ] Notify team of new app URL
- [ ] Update any external links/bookmarks
- [ ] Monitor app performance in new workspace
- [ ] Decommission old app (after verification period)
- [ ] Update GitHub README if needed

---

## 📞 Need Help?

- **Databricks CLI Issues:** `databricks help`
- **Apps Documentation:** https://docs.databricks.com/en/dev-tools/databricks-apps/
- **Genie Documentation:** https://docs.databricks.com/en/genie/
- **Unity Catalog:** https://docs.databricks.com/en/data-governance/unity-catalog/

---

**Created:** January 30, 2026  
**Last Updated:** January 30, 2026
