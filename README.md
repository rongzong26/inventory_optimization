# Supply Chain Inventory Optimization App

A Databricks application for mining supply chain inventory optimization with AI-powered insights using Genie.

## 🎯 Overview

This application provides real-time inventory monitoring and AI-powered recommendations for mining operations. It features:

- **Interactive Dashboard**: Map-based visualization of inventory across multiple mine sites
- **AI-Powered Insights**: Natural language queries using Databricks Genie
- **Real-time Analytics**: KPIs, risk levels, and inventory status tracking
- **Smart Recommendations**: AI-driven part allocation suggestions

## 🏗️ Architecture

```
Databricks Apps Platform
├── SQL Warehouse (Data Access)
├── Genie Space (AI Queries)
└── LLM Endpoint (Recommendations)
```

### Tech Stack

- **Framework**: Dash (Python web framework)
- **Data**: Databricks SQL Warehouse
- **AI**: Databricks Genie + Claude Sonnet 4.5
- **Visualization**: Plotly, Leaflet Maps, AG Grid
- **Deployment**: Databricks Apps

## 📁 Project Structure

```
inventory_optimization_bundle/
├── app/
│   ├── app.py              # Main Dash application
│   ├── layout.py           # UI components
│   ├── utils.py            # Data access utilities
│   ├── chat_assistant.py   # Genie integration
│   ├── prompts.py          # AI prompts
│   └── requirements.txt
├── data/
│   └── gold_master_part_inventory.sql  # Table definition
├── databricks.yml          # Bundle configuration
├── pyproject.toml
└── README.md
```

## 🚀 Deployment

### Prerequisites

- Databricks workspace with Apps enabled
- SQL Warehouse
- Genie space configured with inventory data
- Claude Sonnet endpoint access

### Deploy via Databricks CLI

```bash
# Navigate to bundle directory
cd inventory_optimization_bundle

# Deploy the app
databricks bundle deploy --profile <your-profile>

# Run the app
databricks bundle run inventory-optimization-app --profile <your-profile>
```

### Configuration

The app requires these environment variables (configured in `databricks.yml`):

- `DATABRICKS_WAREHOUSE_HTTP_PATH`: SQL warehouse connection path
- `DATABRICKS_TABLE_NAME`: Inventory table name
- `DATABRICKS_HOST`: Workspace URL (auto-configured)
- `DATABRICKS_TOKEN`: Authentication (auto-configured)

## 📊 Features

### 1. Interactive Map Dashboard

- Real-time inventory status across mine sites
- Color-coded risk levels (Out of Stock, Low Stock, Stocked)
- Click markers for detailed part information

### 2. Inventory Assistant (Genie-Powered)

Natural language queries for inventory data:
- "What parts are low stock?"
- "Which equipment is most at risk?"
- "Show me inventory by site"
- "What parts need reordering at Brisbane Mine?"

**Features:**
- Conversational AI interface
- SQL query generation and execution
- Context-aware follow-up questions
- Real inventory data responses

### 3. AI Allocation Recommendations

- Select inventory items
- Get AI-powered reallocation suggestions
- Optimized transfer and reorder recommendations
- Lead time and vendor analysis

### 4. Data Grid

- Advanced filtering and sorting
- Real-time search
- Export capabilities
- Customizable columns

## 🗄️ Data Model

The app uses a gold table: `gold_master_part_inventory`

**Key Columns:**
- Plant/Site information
- Part details
- Equipment assignments
- Stock levels (on-hand, reserved, safety stock)
- Risk calculations
- Work order data

## 🤖 AI Integration

### Databricks Genie

The Inventory Assistant uses Databricks Genie for natural language to SQL:

```python
# Example query flow
User: "What parts are low stock?"
  ↓
Genie: Generates SQL query
  ↓
Executes against inventory table
  ↓
Returns formatted results
```

**Genie Space Configuration:**
- Space ID: Configured in `chat_assistant.py`
- Tables: `gold_master_part_inventory`
- Permissions: App service principal has `CAN_USE` access

### LLM Recommendations

Uses Claude Sonnet 4.5 for allocation recommendations:
- Analyzes current inventory state
- Considers safety stock levels
- Suggests optimal transfers
- Recommends vendor orders

## 🔒 Security

- OAuth2 authentication via Databricks Apps
- Service principal for data access
- Secure token management
- Row-level security via Unity Catalog

## 📈 Performance

- Data cached on app startup
- Restart app to refresh data from warehouse
- Genie queries: 5-20 seconds
- LLM recommendations: 10-30 seconds

## 🛠️ Development

### Local Setup

```bash
# Install dependencies
pip install -r app/requirements.txt

# Set environment variables
export DATABRICKS_HOST="https://your-workspace.databricks.com"
export DATABRICKS_TOKEN="your-token"
export DATABRICKS_WAREHOUSE_HTTP_PATH="/sql/1.0/warehouses/..."
export DATABRICKS_TABLE_NAME="`catalog`.`schema`.`table`"

# Run locally
python app/app.py
```

### Modifying the App

1. **Update UI**: Edit `layout.py`
2. **Change Data Logic**: Edit `utils.py`
3. **Modify AI Prompts**: Edit `prompts.py`
4. **Update Genie Integration**: Edit `chat_assistant.py`

### Deploy Changes

```bash
databricks bundle deploy --profile <profile>
databricks bundle run inventory-optimization-app --profile <profile>
```

## 📝 Documentation

- **Deployment Guide**: See `DEPLOYMENT_SUMMARY.md`
- **Genie Integration**: See `GENIE_INTEGRATION_COMPLETE.md`
- **Data Migration**: See `TABLE_MIGRATION_GUIDE.md`
- **Dynamic Date**: See `DYNAMIC_DATE_UPDATE.md`

## 🐛 Troubleshooting

### App Not Loading Data

Restart the app to reload cached data:
```bash
databricks bundle run inventory-optimization-app --profile <profile>
```

### Genie Queries Failing

1. Check Genie space permissions
2. Verify table access for app service principal
3. Confirm Genie space ID in `chat_assistant.py`

### LLM Errors

1. Verify Claude endpoint access
2. Check service principal permissions
3. Review prompt length limits

## 🎓 Learning Resources

- [Databricks Apps Documentation](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html)
- [Databricks Genie](https://docs.databricks.com/en/genie/index.html)
- [Dash Framework](https://dash.plotly.com/)
- [Databricks SQL](https://docs.databricks.com/en/sql/index.html)

## 📜 License

Databricks Sample Application

## 👥 Authors

Rong Zong - Databricks

## 🙏 Acknowledgments

- Databricks Genie team
- Databricks Apps team
- Mining operations stakeholders
