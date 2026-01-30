#!/bin/bash

# Migration Script: Move Inventory Optimization App to Target Workspace
# Target: https://adb-984752964297111.11.azuredatabricks.net
# New Catalog/Schema: rz_demo.supply_chain

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  Inventory App Migration to Target     ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Configuration
SOURCE_PROFILE="fe-sandbox-serverless"
TARGET_PROFILE="DEFAULT"
TARGET_CATALOG="rz_demo"
TARGET_SCHEMA="supply_chain"
SOURCE_TABLE="rz-demo-mining.supply-chain.gold_master_part_inventory"
TARGET_TABLE="${TARGET_CATALOG}.${TARGET_SCHEMA}.gold_master_part_inventory"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Source Profile: $SOURCE_PROFILE"
echo "  Target Profile: $TARGET_PROFILE"
echo "  Target Catalog: $TARGET_CATALOG"
echo "  Target Schema: $TARGET_SCHEMA"
echo "  Target Table: $TARGET_TABLE"
echo ""

# Step 1: Authenticate
echo -e "${BLUE}Step 1: Authenticating to target workspace...${NC}"
databricks auth login --profile $TARGET_PROFILE || {
    echo -e "${RED}Authentication failed. Please check your credentials.${NC}"
    exit 1
}
echo -e "${GREEN}✓ Authenticated${NC}"
echo ""

# Step 2: Get SQL Warehouse ID
echo -e "${BLUE}Step 2: Finding SQL Warehouse...${NC}"
WAREHOUSE_ID=$(databricks warehouses list --profile $TARGET_PROFILE --output json | jq -r '.[0].id' 2>/dev/null || echo "")

if [ -z "$WAREHOUSE_ID" ]; then
    echo -e "${RED}No SQL warehouse found. Please create one first.${NC}"
    echo "Run: databricks warehouses create --profile $TARGET_PROFILE"
    exit 1
fi

echo -e "${GREEN}✓ Found SQL Warehouse: $WAREHOUSE_ID${NC}"
echo ""

# Step 3: Update databricks.yml
echo -e "${BLUE}Step 3: Updating databricks.yml with warehouse ID...${NC}"
sed -i.bak "s/id: TBD_UPDATE_AFTER_AUTH/id: $WAREHOUSE_ID/" inventory_optimization_bundle/databricks.yml
echo -e "${GREEN}✓ Updated databricks.yml${NC}"
echo ""

# Step 4: Update app.py
echo -e "${BLUE}Step 4: Updating app.py with warehouse path...${NC}"
WAREHOUSE_PATH="/sql/1.0/warehouses/$WAREHOUSE_ID"
sed -i.bak "s|/sql/1.0/warehouses/TBD_UPDATE_AFTER_AUTH|$WAREHOUSE_PATH|" inventory_optimization_bundle/app/app.py
echo -e "${GREEN}✓ Updated app.py${NC}"
echo ""

# Step 5: Check if data exists in target
echo -e "${BLUE}Step 5: Checking if data exists in target...${NC}"
TABLE_EXISTS=$(databricks warehouses execute \
    --warehouse-id $WAREHOUSE_ID \
    --profile $TARGET_PROFILE \
    --statement "SHOW TABLES IN ${TARGET_CATALOG}.${TARGET_SCHEMA} LIKE 'gold_master_part_inventory'" \
    2>/dev/null | grep -c "gold_master_part_inventory" || echo "0")

if [ "$TABLE_EXISTS" = "0" ]; then
    echo -e "${YELLOW}⚠ Table does not exist in target workspace${NC}"
    echo -e "${YELLOW}Would you like to:${NC}"
    echo "  1) Export and import data from source workspace"
    echo "  2) Skip data migration (I'll create tables manually)"
    echo "  3) Exit and handle data migration separately"
    read -p "Choice (1/2/3): " CHOICE
    
    case $CHOICE in
        1)
            echo -e "${BLUE}Exporting data from source...${NC}"
            # Export to CSV
            databricks sql-warehouse execute \
                --warehouse-id a2188971f887cd35 \
                --profile $SOURCE_PROFILE \
                --statement "SELECT * FROM \`$SOURCE_TABLE\`" \
                --format csv \
                > /tmp/gold_master_part_inventory.csv 2>&1
            
            echo -e "${BLUE}Uploading to target workspace...${NC}"
            databricks fs cp /tmp/gold_master_part_inventory.csv \
                dbfs:/tmp/inventory_migration/ \
                --profile $TARGET_PROFILE
            
            echo -e "${BLUE}Creating table in target...${NC}"
            databricks warehouses execute \
                --warehouse-id $WAREHOUSE_ID \
                --profile $TARGET_PROFILE \
                --statement "
                CREATE TABLE IF NOT EXISTS ${TARGET_TABLE}
                AS SELECT * FROM csv.\`dbfs:/tmp/inventory_migration/gold_master_part_inventory.csv\`
                " 2>&1
            
            echo -e "${GREEN}✓ Data migrated${NC}"
            ;;
        2)
            echo -e "${YELLOW}Skipping data migration. Remember to create tables!${NC}"
            ;;
        3)
            echo -e "${YELLOW}Exiting. Complete data migration and run this script again.${NC}"
            exit 0
            ;;
    esac
else
    echo -e "${GREEN}✓ Table exists in target workspace${NC}"
fi
echo ""

# Step 6: Create/Check Genie Space
echo -e "${BLUE}Step 6: Genie Space Setup${NC}"
echo -e "${YELLOW}⚠ Genie space must be created manually${NC}"
echo ""
echo "Please follow these steps:"
echo "  1. Go to: https://adb-984752964297111.11.azuredatabricks.net/genie"
echo "  2. Click 'Create Space'"
echo "  3. Name it 'Inventory Optimization'"
echo "  4. Add table: ${TARGET_TABLE}"
echo "  5. Copy the Space ID from the URL"
echo ""
read -p "Have you created the Genie space? (y/n): " GENIE_READY

if [ "$GENIE_READY" = "y" ] || [ "$GENIE_READY" = "Y" ]; then
    read -p "Enter Genie Space ID: " GENIE_SPACE_ID
    
    # Update chat_assistant.py
    sed -i.bak "s/GENIE_SPACE_ID = \"TBD_CREATE_NEW_GENIE_SPACE\"/GENIE_SPACE_ID = \"$GENIE_SPACE_ID\"/" \
        inventory_optimization_bundle/app/chat_assistant.py
    
    echo -e "${GREEN}✓ Updated chat_assistant.py with Genie Space ID${NC}"
else
    echo -e "${YELLOW}⚠ You'll need to update chat_assistant.py manually later${NC}"
fi
echo ""

# Step 7: Validate bundle
echo -e "${BLUE}Step 7: Validating bundle configuration...${NC}"
cd inventory_optimization_bundle
databricks bundle validate --profile $TARGET_PROFILE || {
    echo -e "${RED}Bundle validation failed. Check configuration.${NC}"
    exit 1
}
echo -e "${GREEN}✓ Bundle validated${NC}"
echo ""

# Step 8: Deploy
echo -e "${BLUE}Step 8: Deploying to target workspace...${NC}"
databricks bundle deploy --profile $TARGET_PROFILE || {
    echo -e "${RED}Deployment failed. Check errors above.${NC}"
    exit 1
}
echo -e "${GREEN}✓ Bundle deployed${NC}"
echo ""

# Step 9: Start the app
echo -e "${BLUE}Step 9: Starting the app...${NC}"
databricks bundle run inventory-optimization-app --profile $TARGET_PROFILE || {
    echo -e "${RED}Failed to start app. Check logs.${NC}"
    exit 1
}
echo -e "${GREEN}✓ App started${NC}"
echo ""

# Step 10: Get app details
echo -e "${BLUE}Step 10: Getting app details...${NC}"
APP_DETAILS=$(databricks apps get inventory-optimization-app --profile $TARGET_PROFILE --output json 2>/dev/null)
APP_URL=$(echo "$APP_DETAILS" | jq -r '.url // empty')
SERVICE_PRINCIPAL=$(echo "$APP_DETAILS" | jq -r '.service_principal_id // empty')

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Migration Complete! 🎉${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${BLUE}App URL:${NC} $APP_URL"
echo -e "${BLUE}Service Principal ID:${NC} $SERVICE_PRINCIPAL"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Grant Genie permissions to service principal:"
echo "     Go to Genie space → Share → Add service principal: $SERVICE_PRINCIPAL"
echo ""
echo "  2. Test the app:"
echo "     - Visit: $APP_URL"
echo "     - Check map loads"
echo "     - Test Inventory Assistant"
echo ""
echo "  3. Check logs if issues:"
echo "     databricks apps logs inventory-optimization-app --profile $TARGET_PROFILE"
echo ""
echo -e "${GREEN}Migration script completed successfully!${NC}"
