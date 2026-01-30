# Inventory Optimization Bundle - Deployment Summary

## ✅ Deployment Complete

**Date:** January 29, 2026  
**Status:** Successfully Deployed

---

## 📦 Bundle Details

**Bundle Name:** `inventory_optimization_buildathon`  
**App Name:** `inventory-optimization-app`  
**Description:** An inventory optimization app that uses a SQL warehouse

---

## 🔄 Deployment Flow

### Source Workspace
- **Profile:** supply-chain
- **Host:** https://e2-demo-west.cloud.databricks.com
- **Workspace ID:** 2556758628403379
- **Source Path:** `/Users/david.hurley@databricks.com/.bundle/inventory_optimization_buildathon`

### Target Workspace
- **Profile:** fe-sandbox-serverless
- **Host:** https://fe-sandbox-serverless-v7m02q.cloud.databricks.com
- **Target Path:** `/Users/rong.zong@databricks.com/.bundle/inventory_optimization_buildathon`

---

## 🔧 Configuration Changes

### Updated Resources:
1. **SQL Warehouse**
   - Original ID: `75fd8278393d07eb`
   - New ID: `a2188971f887cd35` (Serverless Starter Warehouse)
   - Permission: CAN_USE

2. **Serving Endpoint**
   - Name: `databricks-claude-sonnet-4-5`
   - Permission: CAN_QUERY
   - Status: Available in both workspaces ✓

3. **Workspace Host**
   - Updated to: `https://fe-sandbox-serverless-v7m02q.cloud.databricks.com`

---

## 📱 Deployed Application

**App URL:** https://inventory-optimization-app-7474656208178943.aws.databricksapps.com

**Compute Status:** STARTING (will be ACTIVE shortly)

**Features:**
- Real-time spare parts inventory management across mine sites
- Interactive map visualization with risk levels
- Site-specific KPIs and metrics
- AI-powered recommendations using Claude Sonnet 4.5
- Part reallocation and vendor ordering suggestions

---

## 📁 Bundle Structure

```
inventory_optimization_bundle/
├── app/
│   ├── app.py              # Main Dash application
│   ├── layout.py           # UI components and styling
│   ├── prompts.py          # AI prompt templates
│   ├── utils.py            # Databricks SQL and LLM integration
│   └── requirements.txt    # Python dependencies
├── data/
│   └── gold_master_part_inventory.sql
├── databricks.yml          # Bundle configuration
└── README.md              # Application documentation
```

---

## 🚀 Managing the Deployed App

### Check App Status
```bash
databricks apps get inventory-optimization-app --profile fe-sandbox-serverless
```

### Stop the App
```bash
databricks apps stop inventory-optimization-app --profile fe-sandbox-serverless
```

### Start the App
```bash
databricks apps start inventory-optimization-app --profile fe-sandbox-serverless
```

### Update the App (after changes)
```bash
cd inventory_optimization_bundle
databricks bundle deploy --profile fe-sandbox-serverless
```

### View App Logs
```bash
databricks apps logs inventory-optimization-app --profile fe-sandbox-serverless
```

---

## 📊 Data Requirements

The app expects a table with the following schema:
- Plant/Site information
- Part details
- Equipment information
- Stock levels
- Risk indicators

SQL query available in: `data/gold_master_part_inventory.sql`

---

## 🔐 Permissions

The app has been configured with:
- **Service Principal ID:** 74694297826959
- **OAuth2 Client ID:** 0aa7a7ce-678f-4b36-a44f-de19d7c1b143
- **Creator:** rong.zong@databricks.com

---

## ✅ Verification Steps

1. ✓ Bundle exported from source workspace
2. ✓ Configuration updated for target workspace
3. ✓ SQL Warehouse ID updated
4. ✓ Bundle validated successfully
5. ✓ Bundle deployed to target workspace
6. ✓ App created in target workspace
7. ⏳ App compute starting (in progress)

---

## 📝 Notes

- **Original workspace:** No changes were made to the source bundle in david.hurley@databricks.com
- **Local copy:** Saved in `inventory_optimization_bundle/` directory
- **Deployment mode:** Development
- **App will auto-stop** after period of inactivity to save costs

---

## 🛠️ Troubleshooting

If the app doesn't start properly:

1. Check app logs:
   ```bash
   databricks apps logs inventory-optimization-app --profile fe-sandbox-serverless
   ```

2. Verify SQL warehouse is running:
   ```bash
   databricks warehouses get a2188971f887cd35 --profile fe-sandbox-serverless
   ```

3. Check serving endpoint status:
   ```bash
   databricks serving-endpoints get databricks-claude-sonnet-4-5 --profile fe-sandbox-serverless
   ```

4. Redeploy if needed:
   ```bash
   cd inventory_optimization_bundle
   databricks bundle deploy --profile fe-sandbox-serverless
   ```

---

**Deployment completed by:** Databricks CLI v0.272.0  
**Deployed by:** rong.zong@databricks.com
