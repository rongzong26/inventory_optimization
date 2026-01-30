# Agent Deployment Steps

## Quick Start

I've created everything you need to deploy the Genie Agent with streaming support!

---

## Files Created

1. **`agent/genie_agent.py`** - Agent code with streaming
2. **`agent/requirements.txt`** - Python dependencies  
3. **`agent/deploy_agent.py`** - Deployment script
4. **`Deploy_Genie_Agent.py`** - Databricks notebook (recommended!)

---

## Deployment Options

### Option A: Databricks Notebook (Recommended) ✅

**Steps:**

1. **Upload the notebook** to your workspace:
   ```bash
   databricks workspace import Deploy_Genie_Agent.py \
     /Users/rong.zong@databricks.com/Deploy_Genie_Agent \
     --profile fe-sandbox-serverless \
     --language PYTHON
   ```

2. **Run the notebook** in your workspace:
   - Open: https://fe-sandbox-serverless-v7m02q.cloud.databricks.com
   - Navigate to `/Users/rong.zong@databricks.com/Deploy_Genie_Agent`
   - Click "Run All"

3. **Wait for deployment** (~5-10 minutes)
   - Installs packages
   - Creates agent
   - Deploys to Model Serving
   - Returns endpoint name

4. **Note the endpoint name** for Step 2

---

### Option B: CLI Deployment (Alternative)

**If you prefer command-line:**

```bash
cd inventory_optimization_bundle/agent

# Install dependencies
pip install -r requirements.txt

# Run deployment
python deploy_agent.py
```

---

## What the Agent Does

### Architecture

```
User: "What parts are low stock?"
    ↓
Agent Endpoint (streaming)
    ↓
├─ "📝 Starting query..." (immediately!)
├─ "🔍 Generating SQL..." (~5 sec)
├─ "⚡ Executing query..." (~10 sec)
└─ "✅ Answer: ..." (~15 sec)
```

### Benefits

✅ **Instant feedback** - See "Starting..." immediately  
✅ **Progressive updates** - Status changes every few seconds  
✅ **Better UX** - No more 20-second blackout  
✅ **Cleaner code** - Agent handles complexity  
✅ **Extensible** - Easy to add more tools  

---

## Step 2: Update Dash App (After Agent Deployed)

Once the agent is deployed, I'll update the Dash app to:

1. **Call agent endpoint** instead of Genie API directly
2. **Handle streaming responses** with progressive UI updates
3. **Show status messages** as agent works
4. **Display final answer** when complete

---

## Testing the Agent

**After deployment, test it:**

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Call the agent
response = w.serving_endpoints.query(
    name="inventory-genie-agent-endpoint",
    messages=[{
        "role": "user", 
        "content": "What parts are low stock?"
    }]
)

print(response)
```

**Expected output:**
```json
{
  "answer": "Based on the inventory data, 5 parts are currently low stock...",
  "conversation_id": "abc123",
  "sql": "SELECT ..."
}
```

---

## Troubleshooting

### Issue: "Permission denied to create endpoint"

**Solution:** Ask your workspace admin for Model Serving CREATE permissions, or:
- Use the MLflow model directly (notebook shows how)
- Call model via API instead of serving endpoint

### Issue: "Agent returns empty response"

**Solution:** Check Genie space permissions:
```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
spaces = w.genie.list_spaces()
print([s.space_id for s in spaces])
```

### Issue: "Deployment takes too long"

**Normal:** First deployment takes 5-10 minutes
- Installing dependencies
- Building container
- Starting endpoint

Monitor in UI: Serving → `inventory-genie-agent-endpoint`

---

## Next Steps

**Right now:**

1. ✅ Upload `Deploy_Genie_Agent.py` notebook (command above)
2. ⏳ Run the notebook in your workspace
3. ⏳ Wait for successful deployment
4. ⏳ Tell me the endpoint name, and I'll update the Dash app!

**Then:**

5. I'll update the Dash app to use the agent
6. Deploy updated app
7. Test streaming responses! 🎉

---

## Commands Summary

```bash
# 1. Upload notebook
databricks workspace import Deploy_Genie_Agent.py \
  /Users/rong.zong@databricks.com/Deploy_Genie_Agent \
  --profile fe-sandbox-serverless \
  --language PYTHON

# 2. Open in browser
open "https://fe-sandbox-serverless-v7m02q.cloud.databricks.com/#workspace/Users/rong.zong@databricks.com/Deploy_Genie_Agent"

# 3. Click "Run All" in the notebook

# 4. When done, tell me it succeeded, and I'll update the app!
```

---

**Ready to deploy?** Run the upload command and open the notebook! 🚀
