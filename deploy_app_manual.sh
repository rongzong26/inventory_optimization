#!/bin/bash

# Manual App Deployment Script (workaround for Terraform provider issue)

set -e

PROFILE="DEFAULT"
APP_NAME="inventory-optimization-app"
WORKSPACE_PATH="/Workspace/Users/rong.zong@databricks.com/.bundle/inventory_optimization_buildathon/dev"

echo "Deploying app manually to workaround Terraform provider issue..."

# Upload source code
echo "Uploading source code..."
cd inventory_optimization_bundle

# Create a deployment package
tar -czf /tmp/app_source.tar.gz -C app .

# Upload to workspace
databricks workspace mkdirs "${WORKSPACE_PATH}/files" --profile $PROFILE
databricks fs cp /tmp/app_source.tar.gz "dbfs:${WORKSPACE_PATH}/files/app_source.tar.gz" --profile $PROFILE --overwrite

echo "Creating app via API..."

# Create app using REST API
curl -X POST \
  "https://adb-984752964297111.11.azuredatabricks.net/api/2.0/apps" \
  -H "Authorization: Bearer $(databricks auth token --profile $PROFILE)" \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "name": "${APP_NAME}",
  "description": "An inventory optimization app that uses a SQL warehouse and Genie",
  "source_code_path": "${WORKSPACE_PATH}/files",
  "resources": [
    {
      "name": "sql-warehouse",
      "description": "SQL warehouse for data access",
      "sql_warehouse": {
        "id": "148ccb90800933a1",
        "permission": "CAN_USE"
      }
    },
    {
      "name": "serving-endpoint",
      "description": "LLM endpoint",
      "serving_endpoint": {
        "name": "databricks-claude-sonnet-4-5",
        "permission": "CAN_QUERY"
      }
    }
  ]
}
EOF

echo ""
echo "App created! Starting..."

databricks apps start ${APP_NAME} --profile $PROFILE

echo "Getting app details..."
databricks apps get ${APP_NAME} --profile $PROFILE

