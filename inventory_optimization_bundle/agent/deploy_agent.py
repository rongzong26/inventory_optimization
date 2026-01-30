"""
Deploy the Genie Agent to Databricks Model Serving.

This script deploys the agent as a serving endpoint that the Dash app can call.
"""
import mlflow
from databricks import agents
from databricks.sdk import WorkspaceClient

# Configuration
AGENT_NAME = "inventory-genie-agent"
MODEL_NAME = "inventory_genie_agent_model"
ENDPOINT_NAME = "inventory-genie-agent-endpoint"

def deploy_agent():
    """Deploy the Genie agent to Model Serving"""
    
    print("🚀 Deploying Inventory Genie Agent...")
    
    # Set MLflow tracking
    mlflow.set_experiment(f"/Users/{WorkspaceClient().current_user.me().user_name}/inventory_genie_agent")
    
    # Log the agent
    with mlflow.start_run(run_name="genie_agent_deployment"):
        # Log the agent code
        mlflow.log_artifact("genie_agent.py")
        
        # Log agent as model
        logged_model = mlflow.pyfunc.log_model(
            artifact_path="agent",
            python_model="genie_agent",
            artifacts={"agent_code": "genie_agent.py"},
            pip_requirements="requirements.txt",
            registered_model_name=MODEL_NAME
        )
        
        model_uri = logged_model.model_uri
        print(f"✅ Model logged: {model_uri}")
    
    # Deploy to Model Serving
    print(f"\n📡 Deploying to Model Serving endpoint: {ENDPOINT_NAME}")
    
    deployment_info = agents.deploy(
        model_name=MODEL_NAME,
        model_version=1,
        endpoint_name=ENDPOINT_NAME,
        task="chat",  # Chat task for conversational interface
        config={
            "env": {
                "DATABRICKS_GENIE_SPACE_ID": "01f0fd5cc0c912fcbe49b206c5b467d6"
            }
        }
    )
    
    print(f"\n✅ Agent deployed successfully!")
    print(f"📍 Endpoint: {ENDPOINT_NAME}")
    print(f"🔗 Endpoint URL: {deployment_info.endpoint_url}")
    
    return deployment_info


if __name__ == "__main__":
    try:
        deployment_info = deploy_agent()
        print("\n" + "="*60)
        print("🎉 DEPLOYMENT COMPLETE!")
        print("="*60)
        print(f"\nNext steps:")
        print(f"1. Update your Dash app to call: {ENDPOINT_NAME}")
        print(f"2. Use streaming=True to get progressive updates")
        print(f"3. Test with: 'What parts are low stock?'")
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
