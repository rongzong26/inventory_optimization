#!/bin/bash

# Verification Script: Check target workspace setup before migration

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROFILE="DEFAULT"
CATALOG="rz_demo"
SCHEMA="supply_chain"
TABLE="gold_master_part_inventory"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  Target Workspace Verification         ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Check 1: Authentication
echo -e "${BLUE}[1/6] Checking authentication...${NC}"
databricks auth token --profile $PROFILE > /dev/null 2>&1 && \
    echo -e "${GREEN}✓ Authenticated to target workspace${NC}" || \
    echo -e "${RED}✗ Not authenticated. Run: databricks auth login --profile $PROFILE${NC}"
echo ""

# Check 2: SQL Warehouse
echo -e "${BLUE}[2/6] Checking SQL Warehouses...${NC}"
WAREHOUSES=$(databricks warehouses list --profile $PROFILE --output json 2>/dev/null || echo "[]")
WAREHOUSE_COUNT=$(echo "$WAREHOUSES" | jq '. | length' 2>/dev/null || echo "0")

if [ "$WAREHOUSE_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Found $WAREHOUSE_COUNT SQL warehouse(s)${NC}"
    echo "$WAREHOUSES" | jq -r '.[] | "  - \(.name) (ID: \(.id)) - State: \(.state)"' 2>/dev/null
    WAREHOUSE_ID=$(echo "$WAREHOUSES" | jq -r '.[0].id' 2>/dev/null)
else
    echo -e "${RED}✗ No SQL warehouses found${NC}"
    WAREHOUSE_ID=""
fi
echo ""

# Check 3: Catalog
echo -e "${BLUE}[3/6] Checking catalog ${CATALOG}...${NC}"
if [ -n "$WAREHOUSE_ID" ]; then
    CATALOG_EXISTS=$(databricks warehouses execute \
        --warehouse-id $WAREHOUSE_ID \
        --profile $PROFILE \
        --statement "SHOW CATALOGS LIKE '${CATALOG}'" \
        2>/dev/null | grep -c "$CATALOG" || echo "0")
    
    if [ "$CATALOG_EXISTS" -gt 0 ]; then
        echo -e "${GREEN}✓ Catalog ${CATALOG} exists${NC}"
    else
        echo -e "${RED}✗ Catalog ${CATALOG} not found${NC}"
        echo -e "${YELLOW}  Create with: CREATE CATALOG ${CATALOG};${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Skipping (no warehouse available)${NC}"
fi
echo ""

# Check 4: Schema
echo -e "${BLUE}[4/6] Checking schema ${CATALOG}.${SCHEMA}...${NC}"
if [ -n "$WAREHOUSE_ID" ] && [ "$CATALOG_EXISTS" -gt 0 ]; then
    SCHEMA_EXISTS=$(databricks warehouses execute \
        --warehouse-id $WAREHOUSE_ID \
        --profile $PROFILE \
        --statement "SHOW SCHEMAS IN ${CATALOG} LIKE '${SCHEMA}'" \
        2>/dev/null | grep -c "$SCHEMA" || echo "0")
    
    if [ "$SCHEMA_EXISTS" -gt 0 ]; then
        echo -e "${GREEN}✓ Schema ${CATALOG}.${SCHEMA} exists${NC}"
    else
        echo -e "${RED}✗ Schema ${CATALOG}.${SCHEMA} not found${NC}"
        echo -e "${YELLOW}  Create with: CREATE SCHEMA ${CATALOG}.${SCHEMA};${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Skipping (catalog check failed)${NC}"
fi
echo ""

# Check 5: Table
echo -e "${BLUE}[5/6] Checking table ${CATALOG}.${SCHEMA}.${TABLE}...${NC}"
if [ -n "$WAREHOUSE_ID" ] && [ "$SCHEMA_EXISTS" -gt 0 ]; then
    TABLE_EXISTS=$(databricks warehouses execute \
        --warehouse-id $WAREHOUSE_ID \
        --profile $PROFILE \
        --statement "SHOW TABLES IN ${CATALOG}.${SCHEMA} LIKE '${TABLE}'" \
        2>/dev/null | grep -c "$TABLE" || echo "0")
    
    if [ "$TABLE_EXISTS" -gt 0 ]; then
        echo -e "${GREEN}✓ Table ${CATALOG}.${SCHEMA}.${TABLE} exists${NC}"
        
        # Get row count
        ROW_COUNT=$(databricks warehouses execute \
            --warehouse-id $WAREHOUSE_ID \
            --profile $PROFILE \
            --statement "SELECT COUNT(*) as count FROM ${CATALOG}.${SCHEMA}.${TABLE}" \
            --format json 2>/dev/null | jq -r '.results[0].count' || echo "unknown")
        
        echo -e "  Row count: ${GREEN}${ROW_COUNT}${NC}"
    else
        echo -e "${RED}✗ Table ${CATALOG}.${SCHEMA}.${TABLE} not found${NC}"
        echo -e "${YELLOW}  You'll need to migrate data from source workspace${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Skipping (schema check failed)${NC}"
fi
echo ""

# Check 6: LLM Endpoint
echo -e "${BLUE}[6/6] Checking LLM endpoint...${NC}"
ENDPOINT_EXISTS=$(databricks serving-endpoints get databricks-claude-sonnet-4-5 --profile $PROFILE 2>/dev/null && echo "1" || echo "0")

if [ "$ENDPOINT_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓ Claude Sonnet 4.5 endpoint available${NC}"
else
    echo -e "${YELLOW}⚠ Claude Sonnet endpoint not found (optional feature)${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  Verification Summary                   ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

READY=true

if [ "$WAREHOUSE_COUNT" -eq 0 ]; then
    echo -e "${RED}✗ No SQL warehouse available${NC}"
    READY=false
fi

if [ -n "$WAREHOUSE_ID" ] && [ "$CATALOG_EXISTS" -eq 0 ]; then
    echo -e "${RED}✗ Catalog ${CATALOG} missing${NC}"
    READY=false
fi

if [ -n "$WAREHOUSE_ID" ] && [ "$SCHEMA_EXISTS" -eq 0 ]; then
    echo -e "${RED}✗ Schema ${CATALOG}.${SCHEMA} missing${NC}"
    READY=false
fi

if [ -n "$WAREHOUSE_ID" ] && [ "$TABLE_EXISTS" -eq 0 ]; then
    echo -e "${YELLOW}⚠ Table ${CATALOG}.${SCHEMA}.${TABLE} missing${NC}"
    echo -e "${YELLOW}  Data migration required${NC}"
fi

echo ""

if [ "$READY" = true ]; then
    echo -e "${GREEN}✓ Target workspace is ready for migration!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Create Genie space manually"
    echo "  2. Run: ./migrate_to_target_workspace.sh"
else
    echo -e "${RED}✗ Target workspace setup incomplete${NC}"
    echo ""
    echo -e "${YELLOW}Required actions:${NC}"
    if [ "$WAREHOUSE_COUNT" -eq 0 ]; then
        echo "  - Create or start SQL warehouse"
    fi
    if [ "$CATALOG_EXISTS" -eq 0 ]; then
        echo "  - Create catalog: CREATE CATALOG ${CATALOG};"
    fi
    if [ "$SCHEMA_EXISTS" -eq 0 ]; then
        echo "  - Create schema: CREATE SCHEMA ${CATALOG}.${SCHEMA};"
    fi
    if [ "$TABLE_EXISTS" -eq 0 ]; then
        echo "  - Migrate data table or create new table"
    fi
fi

echo ""
