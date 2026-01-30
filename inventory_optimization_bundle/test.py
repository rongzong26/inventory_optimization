import os
from functools import lru_cache
from databricks import sql
from databricks.sdk.core import Config
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

# Use environment variable or default profile
cfg = Config(profile="e2-demo-west-us")
hostname = cfg.host.replace("https://", "").replace("http://", "") if cfg.host else cfg.host

sql.connect(server_hostname="e2-demo-west.cloud.databricks.com", http_path="/sql/1.0/warehouses/75fd8278393d07eb", credentials_provider=lambda: cfg.authenticate)