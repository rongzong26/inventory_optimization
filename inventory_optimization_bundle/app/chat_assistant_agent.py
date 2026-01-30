"""AI Chat Assistant for Inventory Queries - Powered by Agent Framework"""
import os
import json
import time
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config

# Agent Configuration
AGENT_ENDPOINT_NAME = "inventory-genie-agent-endpoint"
GENIE_SPACE_ID = "01f0fd5cc0c912fcbe49b206c5b467d6"


def query_agent(user_message: str, conversation_history: list = None) -> dict:
    """
    Query the Agent endpoint (which wraps Genie) with streaming support.
    
    Args:
        user_message: User's natural language question
        conversation_history: Previous messages in the conversation
    
    Returns:
        dict with 'response', 'conversation_id', 'sql', and 'success'
    """
    try:
        w = WorkspaceClient()
        
        # Build message history for agent
        messages = []
        
        # Add conversation history if it exists
        if conversation_history:
            for msg in conversation_history:
                if msg.get('role') and msg.get('content'):
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Call the agent endpoint
        response = w.serving_endpoints.query(
            name=AGENT_ENDPOINT_NAME,
            inputs={
                "messages": messages
            }
        )
        
        # Parse the agent's response
        # Agent returns ChatCompletionResponse format:
        # {
        #   "choices": [{
        #     "message": {
        #       "role": "assistant",
        #       "content": '{"answer": "...", "sql": "...", "conversation_id": "..."}'
        #     }
        #   }]
        # }
        
        if hasattr(response, 'choices') and response.choices:
            first_choice = response.choices[0]
            if hasattr(first_choice, 'message'):
                content = first_choice.message.content
                
                # Parse the JSON content from Genie
                try:
                    genie_result = json.loads(content)
                    
                    return {
                        'response': genie_result.get('answer', content),
                        'conversation_id': genie_result.get('conversation_id'),
                        'sql': genie_result.get('sql'),
                        'success': True
                    }
                except json.JSONDecodeError:
                    # If not JSON, return as-is
                    return {
                        'response': content,
                        'success': True
                    }
        
        # Fallback if response format is unexpected
        return {
            'response': str(response),
            'success': True
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        # Check if endpoint exists
        error_msg = str(e)
        if "RESOURCE_DOES_NOT_EXIST" in error_msg or "does not exist" in error_msg.lower():
            return {
                'response': f"⚠️ Agent endpoint not found. The endpoint may still be deploying.\n\n**Status:** Check deployment at https://fe-sandbox-serverless-v7m02q.cloud.databricks.com/serving-endpoints/{AGENT_ENDPOINT_NAME}\n\n**Alternative:** Use the direct Genie integration (revert to previous version).",
                'success': False,
                'error': error_msg
            }
        
        return {
            'response': f"Error calling agent: {error_msg}\n\n**Troubleshooting:**\n- Ensure endpoint is deployed and ready\n- Check endpoint permissions\n- Verify Genie space access",
            'success': False,
            'error': f"{error_msg}\n\n{error_details}"
        }


def get_chat_response(user_message: str, conversation_history: list = None) -> tuple:
    """
    Generate AI response to user's inventory question using Agent Framework.
    
    Args:
        user_message: User's question
        conversation_history: List of previous messages
    
    Returns:
        Tuple of (response_text, genie_conversation_id)
    """
    # Query the agent
    result = query_agent(user_message, conversation_history)
    
    if not result.get('success'):
        return result.get('response', 'An error occurred'), None
    
    # Format response with SQL if available
    response = result.get('response', 'Processing...')
    
    if result.get('sql'):
        # Add SQL query to response for transparency
        response += f"\n\n**Query used:**\n```sql\n{result['sql']}\n```"
    
    return response, result.get('conversation_id')


def get_quick_insights() -> str:
    """Generate quick inventory insights for chat welcome message"""
    return """👋 Hello! I'm your **AI-powered inventory assistant** with Agent + Genie (v3).

I can answer questions about your **actual data** including:

**Data Analysis:**
• Which sites have low stock or outages?
• What parts need immediate reordering?
• Current inventory levels by site or equipment
• Risk level distributions and trends

**Smart Queries:**
• "Show me all out-of-stock items at Brisbane Mine"
• "Which parts are below safety stock?"
• "Compare inventory across all sites"
• "What's the total shortage quantity?"

**Recommendations:**
• Suggest parts to reorder
• Identify critical shortages
• Analyze equipment-specific inventory

💡 **Powered by Databricks Agent + Genie** - Ask me anything about your supply chain inventory!

⏱️ **Note:** First query takes ~15-20 seconds while the agent initializes. Subsequent queries are faster."""
