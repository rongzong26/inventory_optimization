# Inventory Optimization App

An inventory optimization Databricks App that provides real-time supply chain insights powered by Genie AI.

## Features

- **Interactive Dashboard**: Real-time inventory visualization with maps, KPIs, and data grids
- **AI Chat Assistant**: Powered by Databricks Genie for natural language queries
- **SQL Warehouse Integration**: Direct access to Unity Catalog data
- **Risk Analysis**: Automated identification of out-of-stock and low-stock items

## Architecture

### Data Sources
- **Catalog**: `rz-demo-mining`
- **Schema**: `supply-chain`
- **Main Table**: `gold_master_part_inventory`

### App Resources
1. **SQL Warehouse** (ID: `a2188971f887cd35`)
   - Used for data queries and visualization
   - Permission: `CAN_USE`

2. **LLM Serving Endpoint** (`databricks-claude-sonnet-4-5`)
   - Used for AI-powered insights
   - Permission: `CAN_QUERY`

3. **Genie Space** (ID: `01f0fd5cc0c912fcbe49b206c5b467d6`)
   - Powers the AI chat assistant
   - Permission: `CAN_USE` (must be granted manually)
   - **⚠️ Important**: Not automatically provisioned by bundle deployment

## Deployment

### Prerequisites
- Databricks CLI installed and configured
- Access to target workspace with appropriate permissions
- Python 3.8+ for local development

### Deploy to Workspace

```bash
# Set the profile for your target workspace
export DATABRICKS_PROFILE=fe-sandbox-serverless

# Deploy the bundle
databricks bundle deploy --profile $DATABRICKS_PROFILE

# Start the app
databricks bundle run inventory-optimization-app --profile $DATABRICKS_PROFILE
```

### Post-Deployment: Grant Genie Permissions

**⚠️ Critical Step**: After deployment, you must grant the app service principal access to the Genie space.

#### Option 1: Automated Script (Recommended)

```bash
cd inventory_optimization_bundle
chmod +x scripts/grant_genie_permissions.sh
./scripts/grant_genie_permissions.sh
```

Then run the generated notebook in your workspace.

#### Option 2: Manual via UI

1. Open the Genie space:
   ```
   https://fe-sandbox-serverless-v7m02q.cloud.databricks.com/genie/rooms/01f0fd5cc0c912fcbe49b206c5b467d6
   ```

2. Click **"Share"** button

3. Add the service principal:
   ```
   app-34lear inventory-optimization-app
   ```

4. Grant **"Can Use"** permission

5. Click **"Save"**

#### Option 3: Using Databricks CLI

```bash
# Get the service principal name
APP_SP=$(databricks apps get inventory-optimization-app --profile $DATABRICKS_PROFILE --output json | grep service_principal_name | cut -d'"' -f4)

# Use the Grant_Genie_Permissions.py notebook in the workspace
# Located at: /Users/rong.zong@databricks.com/Grant_Genie_Permissions.py
```

### Verify Deployment

1. Check app status:
   ```bash
   databricks apps get inventory-optimization-app --profile $DATABRICKS_PROFILE
   ```

2. Access the app:
   ```
   https://inventory-optimization-app-7474656208178943.aws.databricksapps.com
   ```

3. Test AI Chat:
   - Click "✨ AI Chat" button
   - Type: "How many parts are out of stock?"
   - Press Enter or click Send
   - Should receive Genie-powered response with SQL query

## Development

### Local Setup

```bash
cd inventory_optimization_bundle/app

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABRICKS_WAREHOUSE_HTTP_PATH="/sql/1.0/warehouses/a2188971f887cd35"
export DATABRICKS_TABLE_NAME="`rz-demo-mining`.`supply-chain`.gold_master_part_inventory"

# Run locally (requires Databricks authentication)
python app.py
```

### Project Structure

```
inventory_optimization_bundle/
├── databricks.yml           # Bundle configuration
├── README.md               # This file
├── app/                    # Application source code
│   ├── app.py             # Main Dash application
│   ├── layout.py          # UI components
│   ├── chat_assistant.py  # Genie AI integration
│   ├── utils.py           # Helper functions
│   └── requirements.txt   # Python dependencies
└── scripts/               # Deployment scripts
    └── grant_genie_permissions.sh
```

## Configuration

### Environment Variables

The app uses these environment variables (auto-configured in Databricks Apps):

- `DATABRICKS_WAREHOUSE_HTTP_PATH`: SQL warehouse endpoint
- `DATABRICKS_TABLE_NAME`: Main data table (with backticks for special characters)
- `DATABRICKS_HOST`: Workspace URL
- `DATABRICKS_TOKEN`: Authentication token

### Genie Configuration

Genie space configuration in `app/chat_assistant.py`:

```python
GENIE_SPACE_ID = "01f0fd5cc0c912fcbe49b206c5b467d6"
```

To use a different Genie space:
1. Update `GENIE_SPACE_ID` in `chat_assistant.py`
2. Update comment in `databricks.yml`
3. Update script in `scripts/grant_genie_permissions.sh`
4. Redeploy and grant permissions to the new space

## Features

### AI Chat Assistant

- **Natural Language Queries**: Ask questions in plain English
- **Genie-Powered**: Uses Databricks Genie for intelligent responses
- **SQL Transparency**: Shows the SQL queries used
- **Context Awareness**: Maintains conversation history
- **Keyboard Support**: Press Enter to send, Shift+Enter for new line

**Example queries:**
- "How many parts are out of stock?"
- "Show inventory at Brisbane Mine"
- "Which parts are below safety stock?"
- "Compare inventory across all sites"

### Data Visualization

- **Interactive Map**: Visualize sites with risk-level color coding
- **KPI Cards**: Key metrics at a glance
- **Data Grid**: Sortable, filterable inventory table
- **Risk Analysis**: Automatic categorization (Stocked, Low Stock, Out of Stock)

## Troubleshooting

### App Not Starting

```bash
# Check app status
databricks apps get inventory-optimization-app --profile $DATABRICKS_PROFILE

# Restart app
databricks apps stop inventory-optimization-app --profile $DATABRICKS_PROFILE
databricks apps start inventory-optimization-app --profile $DATABRICKS_PROFILE
```

### Genie Chat Returns Errors

**Error**: "Unable to start conversation. Status: 404"

**Solution**: Grant Genie permissions (see Post-Deployment section above)

**Error**: "Too many requests (429)"

**Solution**: Wait 30 seconds between queries. The app has built-in rate limit handling.

### Data Not Loading

**Error**: "INVALID_IDENTIFIER: rz-demo-mining is invalid"

**Solution**: Ensure table name uses backticks:
```python
TABLE_NAME = "`rz-demo-mining`.`supply-chain`.gold_master_part_inventory"
```

**Error**: "PRINCIPAL_DOES_NOT_EXIST"

**Solution**: Grant data access permissions:
```sql
GRANT USAGE ON CATALOG `rz-demo-mining` TO `account users`;
GRANT USAGE ON SCHEMA `rz-demo-mining`.`supply-chain` TO `account users`;
GRANT SELECT ON TABLE `rz-demo-mining`.`supply-chain`.gold_master_part_inventory TO `account users`;
```

## Maintenance

### Updating the App

```bash
# Make changes to app code
cd inventory_optimization_bundle/app
# Edit files...

# Redeploy
databricks bundle deploy --profile $DATABRICKS_PROFILE
databricks bundle run inventory-optimization-app --profile $DATABRICKS_PROFILE
```

### Checking Logs

```bash
# View app logs (if available in your Databricks CLI version)
databricks apps get inventory-optimization-app --profile $DATABRICKS_PROFILE
```

### Permissions Audit

Periodically verify the service principal has access to:
- ✓ SQL Warehouse (`a2188971f887cd35`)
- ✓ Serving Endpoint (`databricks-claude-sonnet-4-5`)
- ✓ Genie Space (`01f0fd5cc0c912fcbe49b206c5b467d6`)
- ✓ Unity Catalog (`rz-demo-mining.supply-chain.*`)

## Support

For issues or questions:
1. Check this README's Troubleshooting section
2. Review deployment documentation in workspace
3. Check Databricks Apps documentation

## License

Internal use only - Databricks Buildathon 2026
