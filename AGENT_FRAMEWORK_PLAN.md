# Agent Framework Implementation Plan

## Overview

We're creating a **Databricks Agent** that wraps the Genie space, providing:
- ✅ **Streaming responses** - See progress in real-time
- ✅ **Better architecture** - Agent as intermediary
- ✅ **OpenAI compatible** - Standard interface
- ✅ **Scalable** - Can add more tools/agents later

---

## Architecture

### Current (Direct Genie):
```
User Question
    ↓
Dash Callback (blocks 20 sec)
    ↓
Genie REST API
    ↓
[Nothing shows]
    ↓
Response appears all at once
```

### New (Agent Framework):
```
User Question
    ↓
Dash App (non-blocking)
    ↓
Agent Endpoint (streaming!)
    ↓
├─ "📝 Starting query..."
├─ "🔍 Generating SQL..."
├─ "⚡ Executing query..."
└─ "✅ Here's the answer..."
```

---

## Components

### 1. Agent Code (`agent/genie_agent.py`)

**ResponsesAgent with Genie Tool:**
```python
agent = ResponsesAgent(
    name="inventory_genie_agent",
    tools=[query_genie_space],
    system_message="You are an inventory assistant..."
)
```

**Streaming Function:**
```python
def query_genie_space(question: str) -> Iterator[Dict]:
    yield {"status": "starting", "message": "📝 Starting..."}
    # ... call Genie ...
    yield {"status": "executing", "message": "⚡ Executing..."}
    yield {"status": "completed", "response": "..."}
```

### 2. Deployment Script (`agent/deploy_agent.py`)

Deploys agent to Model Serving endpoint:
- Logs agent with MLflow
- Creates serving endpoint
- Configures streaming
- Returns endpoint URL

### 3. Updated Dash App

New callback that consumes streaming responses:
```python
@app.callback(...)
def handle_chat_with_streaming(...):
    # Call agent endpoint
    for chunk in agent_client.stream(user_message):
        # Update UI progressively!
        yield updated_chat_with_status
```

---

## Implementation Steps

### Phase 1: Create & Deploy Agent ⏳

1. ✅ **Create agent code** (`agent/genie_agent.py`)
   - ResponsesAgent with Genie tool
   - Streaming status updates
   - Error handling

2. ✅ **Create deployment script** (`agent/deploy_agent.py`)
   - MLflow logging
   - Model Serving deployment
   - Configuration

3. ⏳ **Deploy agent** (Need to run)
   ```bash
   cd agent
   pip install -r requirements.txt
   python deploy_agent.py
   ```

### Phase 2: Update Dash App ⏳

4. ⏳ **Add agent client** to `chat_assistant.py`
   - Call agent endpoint instead of Genie API
   - Handle streaming responses

5. ⏳ **Update callback** in `app.py`
   - Consume agent stream
   - Show progressive status updates
   - Update chat UI in real-time

6. ⏳ **Test streaming** in app
   - Verify status messages appear
   - Confirm final response shows
   - Test error handling

### Phase 3: Deployment & Testing ⏳

7. ⏳ **Deploy updated app**
   ```bash
   databricks bundle deploy --profile fe-sandbox-serverless
   databricks bundle run inventory-optimization-app --profile fe-sandbox-serverless
   ```

8. ⏳ **End-to-end testing**
   - Test various questions
   - Verify streaming works
   - Check conversation continuity

---

## Benefits of This Approach

### 1. **Streaming Visual Feedback** ✨
- User sees "📝 Starting query..." immediately
- Progressive updates every few seconds
- No more 20-second blackout!

### 2. **Better Architecture**
- Agent as abstraction layer
- Cleaner separation of concerns
- Easier to maintain/extend

### 3. **Future Extensibility**
- Can add RAG tool for documents
- Can add other data sources
- Multi-agent orchestration ready

### 4. **Standard Interface**
- OpenAI-compatible API
- Easy to swap LLMs
- Better integration options

---

## Streaming Dash Integration

**Challenge:** Dash callbacks are synchronous

**Solution:** Use `dcc.Interval` with agent streaming:

```python
# Callback 1: Start agent call
@app.callback(...)
def start_agent_query(...):
    # Call agent (non-blocking)
    agent_call_id = start_agent_stream(question)
    # Enable interval polling
    return ..., agent_call_id, False  # Enable interval

# Callback 2: Poll for stream chunks
@app.callback(
    [Output('chat-messages', 'children', allow_duplicate=True)],
    [Input('stream-poller', 'n_intervals')],
    ...
)
def poll_agent_stream(...):
    # Get next chunk from stream
    chunk = get_next_chunk(agent_call_id)
    
    if chunk["status"] == "executing":
        # Update status message
        return update_status("⚡ Executing...")
    elif chunk["status"] == "completed":
        # Show final response
        return show_final_response(chunk["response"])
```

---

## Configuration

### Environment Variables

```bash
# Genie Space ID (already configured)
GENIE_SPACE_ID=01f0fd5cc0c912fcbe49b206c5b467d6

# Agent Endpoint (after deployment)
AGENT_ENDPOINT_NAME=inventory-genie-agent-endpoint
```

### Permissions Required

- ✅ Model Serving: CREATE_ENDPOINT
- ✅ MLflow: WRITE_MODEL
- ✅ Genie Space: CAN_USE (already granted)

---

## Testing Plan

### Local Testing
```bash
cd agent
python genie_agent.py
# Should see streaming output
```

### Endpoint Testing
```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
response = w.serving_endpoints.query(
    name="inventory-genie-agent-endpoint",
    messages=[{"role": "user", "content": "What parts are low stock?"}]
)
```

### App Testing
1. Open AI Chat
2. Ask: "What parts are low stock?"
3. Verify: See "📝 Starting..." immediately
4. Verify: See "⚡ Executing..." after ~5 sec
5. Verify: See final answer after ~15 sec

---

## Rollback Plan

If agent approach fails:

1. **Keep REST API version** (`chat_assistant.py` with REST API)
2. **Disable agent code** in deployment
3. **Revert to previous stable version**

Backup files:
- `app.py.backup` - Last working version
- `chat_assistant.py` with REST API (current)

---

## Next Steps

**Right now:**
1. Deploy the agent to Model Serving
2. Update Dash app to use agent
3. Test streaming in the app

**Ready to proceed?** Run the deployment script! 🚀
