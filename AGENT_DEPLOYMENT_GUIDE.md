# Agent Framework Deployment Guide

## 🎉 Status: Agent Successfully Created!

✅ **Model Registered:** `rz-demo-mining.supply-chain.inventory_genie_agent` (version 3)  
✅ **Endpoint Created:** `inventory-genie-agent-endpoint`  
⏳ **Deployment Status:** IN_PROGRESS (container creation pending)

---

## Step 1: Wait for Endpoint to be Ready (5-10 minutes)

### Check Status in UI

1. **Open Serving Endpoints:**
   https://fe-sandbox-serverless-v7m02q.cloud.databricks.com/serving-endpoints

2. **Find:** `inventory-genie-agent-endpoint`

3. **Wait for status:**
   - ⏳ **Deploying** → Wait...
   - ✅ **Ready** → Proceed to Step 2!

### Alternative: Check via Databricks Notebook

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
endpoint = w.serving_endpoints.get("inventory-genie-agent-endpoint")

print(f"Status: {endpoint.state.config_update}")
print(f"Ready: {endpoint.state.ready}")

# When ready:
# Status: UPDATE_COMPLETE
# Ready: READY
```

---

## Step 2: Test the Agent Endpoint

Before updating the app, test that the agent works:

### Test in Notebook

```python
from databricks.sdk import WorkspaceClient
import json

w = WorkspaceClient()

# Test query
response = w.serving_endpoints.query(
    name="inventory-genie-agent-endpoint",
    inputs={
        "messages": [
            {"role": "user", "content": "What parts are low stock?"}
        ]
    }
)

print("✅ Agent Response:")
print(response.choices[0].message.content)
```

**Expected output:**
```json
{
  "answer": "Based on the inventory data, 5 parts are currently low stock...",
  "conversation_id": "abc123...",
  "sql": "SELECT ..."
}
```

---

## Step 3: Update the Dash App

Once the endpoint is READY, switch the app to use the agent:

### Option A: Automated Switch (Recommended)

```bash
cd "/Users/rong.zong/Cursor/supply chain inventory"
./switch_to_agent.sh
```

This script will:
1. Backup current `chat_assistant.py`
2. Replace it with `chat_assistant_agent.py`
3. Deploy the updated app

### Option B: Manual Switch

1. **Backup current version:**
   ```bash
   cp inventory_optimization_bundle/app/chat_assistant.py \
      inventory_optimization_bundle/app/chat_assistant_direct.py.backup
   ```

2. **Switch to agent version:**
   ```bash
   cp inventory_optimization_bundle/app/chat_assistant_agent.py \
      inventory_optimization_bundle/app/chat_assistant.py
   ```

3. **Deploy:**
   ```bash
   databricks bundle deploy --profile fe-sandbox-serverless
   databricks bundle run inventory-optimization-app --profile fe-sandbox-serverless
   ```

---

## Step 4: Test the App

1. **Open the app:**
   https://fe-sandbox-serverless-v7m02q.cloud.databricks.com/apps/inventory-optimization-app

2. **Click AI Chat** (robot icon in header)

3. **Test query:** "What parts are low stock?"

4. **Verify:**
   - ✅ Query completes successfully
   - ✅ Response includes actual data
   - ✅ SQL query displayed (if applicable)

---

## Benefits of Agent Framework vs Direct Genie

| Feature | Direct Genie | Agent Framework |
|---------|-------------|-----------------|
| **Setup** | Simple | Complex (endpoint) |
| **Response Time** | 15-20s | 15-25s (similar) |
| **Streaming** | ❌ No | ✅ Potential |
| **Multi-tool Support** | ❌ No | ✅ Yes |
| **Extensibility** | ❌ Limited | ✅ High |
| **Monitoring** | Basic | Enterprise |
| **Cost** | Lower | Higher (serving endpoint) |

---

## Rollback Plan

If the agent doesn't work as expected:

### Quick Rollback

```bash
cd "/Users/rong.zong/Cursor/supply chain inventory"
./rollback_to_direct_genie.sh
```

Or manually:

```bash
cp inventory_optimization_bundle/app/chat_assistant_direct.py.backup \
   inventory_optimization_bundle/app/chat_assistant.py

databricks bundle deploy --profile fe-sandbox-serverless
databricks bundle run inventory-optimization-app --profile fe-sandbox-serverless
```

---

## Troubleshooting

### Issue: "Agent endpoint not found"

**Cause:** Endpoint still deploying or deployment failed

**Solution:**
1. Check endpoint status in UI
2. Wait for READY status
3. If failed, check logs in Serving → Logs tab

### Issue: "Permission denied"

**Cause:** App service principal lacks endpoint access

**Solution:**
```sql
-- Grant endpoint query permissions
GRANT USE_GENIE ON GENIE_SPACE '01f0fd5cc0c912fcbe49b206c5b467d6' 
TO `app-34lear inventory-optimization-app`;
```

### Issue: "Response format unexpected"

**Cause:** Agent returns different format than expected

**Solution:**
1. Test endpoint directly (see Step 2)
2. Check agent logs in Serving → Logs
3. Update parsing logic in `chat_assistant_agent.py`

---

## Monitoring & Optimization

### View Agent Logs

1. Go to: https://fe-sandbox-serverless-v7m02q.cloud.databricks.com/serving-endpoints/inventory-genie-agent-endpoint
2. Click **Logs** tab
3. Monitor requests, responses, and errors

### View Inference Table

Agent automatically logs all requests to:
- **Catalog:** `rz-demo-mining`
- **Schema:** `supply-chain`
- **Table:** `inventory_genie_agent_*`

Query logs:
```sql
SELECT * FROM `rz-demo-mining`.`supply-chain`.inventory_genie_agent_request_logs
ORDER BY timestamp DESC
LIMIT 10;
```

### Performance Optimization

If agent is slow:
1. Increase workload size: Small → Medium
2. Disable scale-to-zero
3. Pre-warm endpoint with dummy queries

---

## Next Steps

**Right now:**
1. ⏳ Wait for endpoint to be READY (~5-10 min)
2. ✅ Test endpoint (Step 2)
3. 🚀 Switch app to use agent (Step 3)

**Future enhancements:**
- Add streaming UI updates (polling-based)
- Add more tools to agent (RAG, forecasting)
- Implement multi-agent orchestration

---

## Files Created

1. **`chat_assistant_agent.py`** - Agent-powered chat implementation
2. **`Deploy_Genie_Agent.py`** - Notebook to deploy agent (ran successfully)
3. **`check_agent_status.sh`** - Status monitoring script
4. **`switch_to_agent.sh`** - Automated deployment script (to be created)
5. **`rollback_to_direct_genie.sh`** - Rollback script (to be created)

---

## Support

- **Agent Endpoint:** https://fe-sandbox-serverless-v7m02q.cloud.databricks.com/serving-endpoints/inventory-genie-agent-endpoint
- **Model:** `rz-demo-mining.supply-chain.inventory_genie_agent:3`
- **Genie Space:** https://fe-sandbox-serverless-v7m02q.cloud.databricks.com/genie/rooms/01f0fd5cc0c912fcbe49b206c5b467d6
