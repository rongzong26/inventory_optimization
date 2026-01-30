"""Databricks utilities: SQL connection and LLM calls"""
import os
from functools import lru_cache
from databricks import sql
from databricks.sdk.core import Config
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

# Use environment variable or default profile
cfg = Config()
hostname = cfg.host.replace("https://", "").replace("http://", "") if cfg.host else cfg.host

@lru_cache(maxsize=1)
def get_connection(http_path):
    """Create cached Databricks SQL connection"""
    return sql.connect(server_hostname=hostname, http_path=http_path, 
                      credentials_provider=lambda: cfg.authenticate)

def read_table(table_name, conn):
    """Read table data into pandas DataFrame"""
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        return cursor.fetchall_arrow().to_pandas()

def call_databricks_llm(prompt, endpoint_name="databricks-claude-sonnet-4-5", max_tokens=3000):
    """Call Databricks LLM serving endpoint with prompt"""
    try:
        w = WorkspaceClient()
        response = w.serving_endpoints.query(
            name=endpoint_name,
            messages=[
                ChatMessage(
                    role=ChatMessageRole.SYSTEM,
                    content="You are a supply chain optimization expert. Provide actionable recommendations for inventory management and part allocation."
                ),
                ChatMessage(
                    role=ChatMessageRole.USER,
                    content=prompt
                )
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling LLM: {str(e)}"


