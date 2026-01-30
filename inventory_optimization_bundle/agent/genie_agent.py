"""
Databricks Agent that wraps Genie for streaming inventory queries.

This agent provides a streaming interface to the Genie space,
allowing progressive status updates as Genie processes queries.
"""
import os
from databricks.sdk import WorkspaceClient
from databricks_agent_framework import ResponsesAgent
from typing import Iterator, Dict, Any

# Genie Space Configuration
GENIE_SPACE_ID = "01f0fd5cc0c912fcbe49b206c5b467d6"


def query_genie_space(question: str, conversation_id: str = None) -> Iterator[Dict[str, Any]]:
    """
    Tool function that queries the Genie space and yields streaming updates.
    
    Args:
        question: User's natural language question about inventory
        conversation_id: Optional conversation ID to continue existing conversation
    
    Yields:
        Dict with status updates and final response
    """
    w = WorkspaceClient()
    
    try:
        # Yield initial status
        yield {
            "status": "starting",
            "message": "📝 Starting Genie query..."
        }
        
        # Start or continue conversation
        if not conversation_id:
            # Start new conversation
            yield {
                "status": "creating_conversation",
                "message": "🔄 Creating new conversation..."
            }
            
            result = w.genie.start_conversation(
                space_id=GENIE_SPACE_ID,
                content=question
            )
            conversation_id = result.conversation_id
            message_id = result.message_id
        else:
            # Continue existing conversation
            yield {
                "status": "sending_message",
                "message": "💬 Sending message to Genie..."
            }
            
            result = w.genie.create_message(
                space_id=GENIE_SPACE_ID,
                conversation_id=conversation_id,
                content=question
            )
            message_id = result.message_id
        
        # Poll for response with status updates
        yield {
            "status": "waiting",
            "message": "⏳ Waiting for Genie to process..."
        }
        
        # Wait for completion
        response = w.genie.get_message(
            space_id=GENIE_SPACE_ID,
            conversation_id=conversation_id,
            message_id=message_id
        )
        
        # Check status and yield updates
        status = getattr(response, 'status', 'UNKNOWN')
        
        if status == 'QUERY_GENERATION':
            yield {
                "status": "generating_query",
                "message": "🔍 Generating SQL query..."
            }
        
        if status == 'EXECUTING_QUERY':
            yield {
                "status": "executing",
                "message": "⚡ Executing query on your data..."
            }
        
        # Extract final response
        response_text = None
        sql_query = None
        
        # Try to extract from attachments
        if hasattr(response, 'attachments') and response.attachments:
            for attachment in response.attachments:
                if hasattr(attachment, 'text') and attachment.text:
                    text_obj = attachment.text
                    if hasattr(text_obj, 'content'):
                        response_text = text_obj.content
                    elif isinstance(text_obj, str):
                        response_text = text_obj
                    
                    if response_text and response_text != question:
                        break
                
                # Extract SQL if available
                if hasattr(attachment, 'query') and attachment.query:
                    if hasattr(attachment.query, 'query'):
                        sql_query = attachment.query.query
        
        # Fallback
        if not response_text or response_text == question:
            if hasattr(response, 'description') and response.description:
                response_text = response.description
            else:
                response_text = "Query completed. Check Genie space for results."
        
        # Yield final response
        yield {
            "status": "completed",
            "message": "✅ Complete!",
            "response": response_text,
            "sql": sql_query,
            "conversation_id": conversation_id
        }
        
    except Exception as e:
        yield {
            "status": "error",
            "message": f"❌ Error: {str(e)}",
            "error": str(e)
        }


# Create the ResponsesAgent
agent = ResponsesAgent(
    name="inventory_genie_agent",
    description="AI agent for querying supply chain inventory data using Genie",
    tools=[
        {
            "name": "query_genie_space",
            "description": "Query the Genie space for inventory data using natural language",
            "function": query_genie_space,
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Natural language question about inventory"
                    },
                    "conversation_id": {
                        "type": "string",
                        "description": "Optional conversation ID to continue existing conversation"
                    }
                },
                "required": ["question"]
            }
        }
    ],
    system_message="""You are an AI assistant for supply chain inventory management.
    
You have access to a Genie space that contains inventory data for mining operations.
When users ask questions about inventory, use the query_genie_space tool to get answers.

Always:
- Use the tool for any data-related questions
- Provide clear, actionable responses
- Include SQL queries when relevant
- Maintain conversation context for follow-up questions

Example questions you can answer:
- What parts are low stock?
- Which sites have outages?
- Show inventory at Brisbane Mine
- What's the total shortage quantity?
"""
)


def predict(messages: list, stream: bool = True) -> Iterator[str]:
    """
    Prediction function for the agent.
    
    Args:
        messages: List of chat messages
        stream: Whether to stream responses (default True)
    
    Yields:
        Streaming response chunks
    """
    # Get the latest user message
    user_message = messages[-1]["content"] if messages else ""
    
    # Extract conversation ID from previous messages if available
    conversation_id = None
    for msg in messages[:-1]:
        if isinstance(msg.get("content"), dict) and "conversation_id" in msg["content"]:
            conversation_id = msg["content"]["conversation_id"]
    
    # Query Genie with streaming
    for update in query_genie_space(user_message, conversation_id):
        if stream:
            # Yield status updates
            if update["status"] in ["starting", "creating_conversation", "sending_message", "waiting", "generating_query", "executing"]:
                yield f"data: {update['message']}\n\n"
            
            # Yield final response
            elif update["status"] == "completed":
                response = update["response"]
                if update.get("sql"):
                    response += f"\n\n**Query used:**\n```sql\n{update['sql']}\n```"
                yield f"data: {response}\n\n"
                yield "data: [DONE]\n\n"
            
            # Yield errors
            elif update["status"] == "error":
                yield f"data: {update['message']}\n\n"
                yield "data: [DONE]\n\n"
        else:
            # Non-streaming: accumulate and return final response
            if update["status"] == "completed":
                response = update["response"]
                if update.get("sql"):
                    response += f"\n\n**Query used:**\n```sql\n{update['sql']}\n```"
                return response


if __name__ == "__main__":
    # Test the agent locally
    test_messages = [
        {"role": "user", "content": "What parts are low stock?"}
    ]
    
    print("Testing agent with streaming...")
    for chunk in predict(test_messages, stream=True):
        print(chunk, end="", flush=True)
