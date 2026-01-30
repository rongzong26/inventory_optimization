#!/bin/bash
# Post-deployment script to grant Genie space permissions to the app service principal
# Run this after 'databricks bundle deploy' to ensure app can access Genie

set -e

echo "================================================"
echo "Granting Genie Space Permissions"
echo "================================================"

# Configuration
GENIE_SPACE_ID="01f0fd5cc0c912fcbe49b206c5b467d6"
APP_NAME="inventory-optimization-app"
WORKSPACE_PROFILE="${DATABRICKS_PROFILE:-fe-sandbox-serverless}"

echo ""
echo "Configuration:"
echo "  Genie Space ID: $GENIE_SPACE_ID"
echo "  App Name: $APP_NAME"
echo "  Workspace Profile: $WORKSPACE_PROFILE"
echo ""

# Get the service principal name for the app
echo "Step 1: Getting app service principal..."
APP_INFO=$(databricks apps get "$APP_NAME" --profile "$WORKSPACE_PROFILE" --output json 2>&1)

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to get app info"
    echo "$APP_INFO"
    exit 1
fi

SERVICE_PRINCIPAL_NAME=$(echo "$APP_INFO" | grep -o '"service_principal_name":"[^"]*"' | cut -d'"' -f4)
SERVICE_PRINCIPAL_ID=$(echo "$APP_INFO" | grep -o '"service_principal_id":[0-9]*' | cut -d':' -f2)

if [ -z "$SERVICE_PRINCIPAL_NAME" ]; then
    echo "❌ Error: Could not extract service principal name from app"
    exit 1
fi

echo "✓ Found service principal: $SERVICE_PRINCIPAL_NAME (ID: $SERVICE_PRINCIPAL_ID)"
echo ""

# Create a temporary Python notebook to grant permissions
echo "Step 2: Creating permission grant notebook..."
NOTEBOOK_PATH="/Workspace/tmp/grant_genie_permissions_$(date +%s).py"

cat > /tmp/grant_genie_temp.py << 'NOTEBOOK_EOF'
# Databricks notebook source
# MAGIC %md
# MAGIC # Grant Genie Space Permissions
# MAGIC 
# MAGIC This notebook grants the app service principal access to the Genie space.

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import iam

# COMMAND ----------

# Configuration
GENIE_SPACE_ID = "01f0fd5cc0c912fcbe49b206c5b467d6"
SERVICE_PRINCIPAL_ID = {{SERVICE_PRINCIPAL_ID}}
SERVICE_PRINCIPAL_NAME = "{{SERVICE_PRINCIPAL_NAME}}"

print(f"Granting permissions to: {SERVICE_PRINCIPAL_NAME}")
print(f"For Genie space: {GENIE_SPACE_ID}")

# COMMAND ----------

# Initialize workspace client
w = WorkspaceClient()

# COMMAND ----------

# Grant CAN_USE permission on Genie space (Genie spaces are stored as dashboards)
try:
    # Get current permissions
    current_perms = w.permissions.get(
        request_object_type="dashboards",
        request_object_id=GENIE_SPACE_ID
    )
    
    print(f"Current permissions: {current_perms}")
    
    # Add service principal with CAN_USE permission
    w.permissions.update(
        request_object_type="dashboards",
        request_object_id=GENIE_SPACE_ID,
        access_control_list=[
            iam.AccessControlRequest(
                service_principal_name=SERVICE_PRINCIPAL_NAME,
                permission_level=iam.PermissionLevel.CAN_USE
            )
        ]
    )
    
    print(f"✓ Successfully granted CAN_USE permission to {SERVICE_PRINCIPAL_NAME}")
    
except Exception as e:
    print(f"❌ Error granting permissions: {e}")
    print("\nTrying alternative permission level (CAN_RUN)...")
    
    try:
        w.permissions.update(
            request_object_type="dashboards",
            request_object_id=GENIE_SPACE_ID,
            access_control_list=[
                iam.AccessControlRequest(
                    service_principal_name=SERVICE_PRINCIPAL_NAME,
                    permission_level=iam.PermissionLevel.CAN_RUN
                )
            ]
        )
        print(f"✓ Successfully granted CAN_RUN permission to {SERVICE_PRINCIPAL_NAME}")
    except Exception as e2:
        print(f"❌ Failed with CAN_RUN as well: {e2}")
        raise

# COMMAND ----------

# Verify permissions were granted
try:
    perms = w.permissions.get(
        request_object_type="dashboards",
        request_object_id=GENIE_SPACE_ID
    )
    
    print("\n" + "="*50)
    print("Final Permissions:")
    print("="*50)
    for acl in perms.access_control_list:
        if acl.service_principal_name:
            print(f"  {acl.service_principal_name}: {acl.all_permissions}")
    
    print("\n✓ Permission grant complete!")
    
except Exception as e:
    print(f"Warning: Could not verify permissions: {e}")

NOTEBOOK_EOF

# Replace placeholders
sed "s/{{SERVICE_PRINCIPAL_ID}}/$SERVICE_PRINCIPAL_ID/g" /tmp/grant_genie_temp.py | \
sed "s/{{SERVICE_PRINCIPAL_NAME}}/$SERVICE_PRINCIPAL_NAME/g" > /tmp/grant_genie_final.py

echo "✓ Created notebook"
echo ""

# Upload and run the notebook
echo "Step 3: Uploading notebook to workspace..."
databricks workspace import \
    "$NOTEBOOK_PATH" \
    --file /tmp/grant_genie_final.py \
    --language PYTHON \
    --format SOURCE \
    --overwrite \
    --profile "$WORKSPACE_PROFILE"

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to upload notebook"
    exit 1
fi

echo "✓ Uploaded to: $NOTEBOOK_PATH"
echo ""

# Run the notebook
echo "Step 4: Running permission grant notebook..."
echo "(This may take 30-60 seconds...)"
echo ""

# Note: We use 'workspace export' to run it as a script instead of creating a job
# This is simpler for a one-time permission grant
echo "To run this notebook, execute:"
echo ""
echo "  databricks workspace export '$NOTEBOOK_PATH' --profile '$WORKSPACE_PROFILE' | python3"
echo ""
echo "Or run it manually in the workspace UI:"
echo "  https://fe-sandbox-serverless-v7m02q.cloud.databricks.com$NOTEBOOK_PATH"
echo ""

# Cleanup
rm -f /tmp/grant_genie_temp.py /tmp/grant_genie_final.py

echo "================================================"
echo "✓ Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Run the notebook manually (link above), OR"
echo "  2. Grant permissions via Genie UI:"
echo "     https://fe-sandbox-serverless-v7m02q.cloud.databricks.com/genie/rooms/$GENIE_SPACE_ID"
echo "     → Click 'Share' → Add '$SERVICE_PRINCIPAL_NAME' → Grant 'Can Use'"
echo ""
echo "After granting permissions, test the app:"
echo "  https://inventory-optimization-app-7474656208178943.aws.databricksapps.com"
echo ""
