"""AI Chat Assistant for Inventory Queries - Direct Genie Integration (Working Version)"""
import os
import time
import requests
from databricks.sdk.core import Config

# Genie Space Configuration  
GENIE_SPACE_ID = "01f0fd5cc0c912fcbe49b206c5b467d6"


def query_genie(user_message: str, conversation_id: str = None) -> dict:
    """
    Query Genie API directly with user's question using REST API
    
    Args:
        user_message: User's natural language question
        conversation_id: Optional conversation ID to continue existing conversation
    
    Returns:
        dict with 'response', 'conversation_id', 'success', and optional 'sql'
    """
    try:
        # Get config for authentication
        cfg = Config()
        hostname = cfg.host if cfg.host else None
        
        if not hostname:
            return {
                'response': "Configuration error: Unable to determine workspace URL",
                'success': False
            }
        
        # Ensure hostname has proper format
        if not hostname.startswith('http'):
            hostname = f"https://{hostname}"
        
        # Get authentication token
        auth_provider = cfg.authenticate()
        
        # Call the auth provider to get the actual token
        if callable(auth_provider):
            token = auth_provider()
        else:
            # If it's already a dict with token
            token = auth_provider.get('Authorization', '').replace('Bearer ', '') if isinstance(auth_provider, dict) else str(auth_provider)
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Start new conversation or continue existing one
        if not conversation_id:
            # Create a new conversation
            url = f"{hostname}/api/2.0/genie/spaces/{GENIE_SPACE_ID}/start-conversation"
            payload = {'content': user_message}
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                error_detail = response.text
                return {
                    'response': f"Unable to start conversation. Status: {response.status_code}.",
                    'success': False,
                    'error': error_detail
                }
            
            result = response.json()
            conversation_id = result.get('conversation_id')
            message_id = result.get('message_id')
        else:
            # Continue existing conversation
            url = f"{hostname}/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conversation_id}/messages"
            payload = {'content': user_message}
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                error_detail = response.text
                return {
                    'response': f"Unable to send message. Status: {response.status_code}. Detail: {error_detail}",
                    'success': False,
                    'error': error_detail
                }
            
            result = response.json()
            message_id = result.get('id')
        
        # Poll for response (Genie processes asynchronously)
        max_wait = 45  # seconds
        start_time = time.time()
        poll_interval = 3  # seconds
        
        while time.time() - start_time < max_wait:
            try:
                # Get message status
                status_url = f"{hostname}/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conversation_id}/messages/{message_id}"
                status_response = requests.get(status_url, headers=headers, timeout=10)
                
                if status_response.status_code == 200:
                    message_data = status_response.json()
                    status = message_data.get('status')
                    
                    if status in ['COMPLETED', 'EXECUTING_QUERY']:
                        response_text = None
                        sql_query = None
                        
                        # Extract SQL query if available
                        if 'query' in message_data and message_data['query']:
                            query_obj = message_data['query']
                            if isinstance(query_obj, dict):
                                sql_query = query_obj.get('query') or query_obj.get('sql')
                            else:
                                sql_query = str(query_obj)
                        
                        # Look for response in attachments
                        if 'attachments' in message_data and message_data['attachments']:
                            attachments = message_data['attachments']
                            for attachment in attachments:
                                # Text response attachment
                                if attachment.get('type') == 'text' or 'text' in attachment:
                                    if isinstance(attachment.get('text'), dict):
                                        response_text = attachment['text'].get('content') or attachment['text'].get('text')
                                    else:
                                        response_text = attachment.get('text')
                                    if response_text and response_text != user_message:
                                        break
                                # Query result attachment
                                elif attachment.get('type') == 'query':
                                    query_result = attachment.get('query', {})
                                    response_text = query_result.get('description') or query_result.get('result')
                                    if response_text and response_text != user_message:
                                        break
                                # Statement execution result
                                elif attachment.get('type') == 'statement_execution_result':
                                    result_data = attachment.get('statement_execution_result', {})
                                    response_text = result_data.get('text') or result_data.get('description')
                                    if response_text and response_text != user_message:
                                        break
                        
                        # If no response text found, check other fields
                        if not response_text or response_text == user_message:
                            if 'result' in message_data and message_data['result'] != user_message:
                                response_text = message_data['result']
                            elif 'description' in message_data and message_data['description'] != user_message:
                                response_text = message_data['description']
                            else:
                                response_text = "Query completed. Check the Genie space for results."
                        
                        return {
                            'response': response_text,
                            'conversation_id': conversation_id,
                            'sql': sql_query,
                            'success': True
                        }
                    
                    elif status == 'FAILED':
                        error_msg = message_data.get('error', 'Query failed')
                        return {
                            'response': f"Query failed: {error_msg}",
                            'conversation_id': conversation_id,
                            'success': False
                        }
                
                elif status_response.status_code == 429:
                    # Rate limited - wait longer before retrying
                    time.sleep(5)
                    continue
            
            except Exception as poll_error:
                # Continue polling
                pass
            
            time.sleep(poll_interval)
        
        # Timeout
        return {
            'response': "The query is taking longer than expected. Please try a simpler question or try again.",
            'conversation_id': conversation_id,
            'success': False
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return {
            'response': f"Error: {str(e)}",
            'success': False,
            'error': f"{str(e)}\n\n{error_details}"
        }


def get_chat_response(user_message: str, conversation_history: list = None) -> tuple:
    """
    Generate AI response to user's inventory question using Direct Genie
    
    Args:
        user_message: User's question
        conversation_history: List of previous messages with 'genie_conversation_id' if exists
    
    Returns:
        Tuple of (response_text, genie_conversation_id)
    """
    # Extract Genie conversation ID from history if it exists
    genie_conversation_id = None
    if conversation_history:
        for msg in conversation_history:
            if msg.get('genie_conversation_id'):
                genie_conversation_id = msg['genie_conversation_id']
                break
    
    # Query Genie using REST API
    result = query_genie(user_message, genie_conversation_id)
    
    if not result.get('success'):
        return result.get('response', 'An error occurred'), genie_conversation_id
    
    # Format response with SQL if available
    response = result.get('response', 'Processing...')
    
    if result.get('sql'):
        # Add SQL query to response for transparency
        response += f"\n\n**Query used:**\n```sql\n{result['sql']}\n```"
    
    return response, result.get('conversation_id')


def get_quick_insights() -> str:
    """Generate quick inventory insights for chat welcome message"""
    return """👋 Hello! I'm your **Genie-powered AI assistant** for supply chain inventory.

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

💡 **Powered by Databricks Genie** - Ask me anything about your supply chain inventory!

⏱️ **Note:** Responses take 5-20 seconds to process."""
