"""
Camunda MCP Server using FastMCP
Provides tools to interact with Camunda BPM Platform via REST API
"""

import os
from typing import Optional, Dict, List, Any
import httpx
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Camunda BPM")

# Camunda configuration
CAMUNDA_URL = os.getenv("CAMUNDA_URL", "http://localhost:8080/engine-rest")
CAMUNDA_USER = os.getenv("CAMUNDA_USER", "demo")
CAMUNDA_PASSWORD = os.getenv("CAMUNDA_PASSWORD", "demo")


def get_auth():
    """Get authentication tuple for Camunda API"""
    return (CAMUNDA_USER, CAMUNDA_PASSWORD) if CAMUNDA_USER and CAMUNDA_PASSWORD else None


async def camunda_request(
    endpoint: str,
    method: str = "GET",
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None
) -> Any:
    """Make a request to Camunda REST API"""
    url = f"{CAMUNDA_URL}/{endpoint}"
    auth = get_auth()
    
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=method,
            url=url,
            auth=auth,
            params=params,
            json=json_data,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json() if response.text else None


@mcp.tool()
async def list_process_definitions(
    key: Optional[str] = None,
    name: Optional[str] = None,
    latest_version: bool = True,
    max_results: int = 50
) -> List[Dict]:
    """
    List all BPMN process definitions from Camunda.
    
    Args:
        key: Filter by process definition key (partial match)
        name: Filter by process definition name (partial match)
        latest_version: Only return latest versions (default: True)
        max_results: Maximum number of results to return (default: 50)
    
    Returns:
        List of process definitions with their metadata
    """
    params = {
        "maxResults": max_results,
        "latestVersion": latest_version
    }
    
    if key:
        params["keyLike"] = f"%{key}%"
    if name:
        params["nameLike"] = f"%{name}%"
    
    definitions = await camunda_request("process-definition", params=params)
    return definitions


@mcp.tool()
async def get_process_definition(definition_id: str) -> Dict:
    """
    Get details of a specific process definition.
    
    Args:
        definition_id: The ID of the process definition
    
    Returns:
        Process definition details
    """
    return await camunda_request(f"process-definition/{definition_id}")


@mcp.tool()
async def start_process_instance(
    key: str,
    business_key: Optional[str] = None,
    variables: Optional[Dict[str, Any]] = None
) -> Dict:
    """
    Start a new process instance by process definition key.
    
    Args:
        key: The key of the process definition
        business_key: Optional business key for the process instance
        variables: Optional process variables as dict {name: value}
    
    Returns:
        Created process instance details
    """
    payload = {}
    
    if business_key:
        payload["businessKey"] = business_key
    
    if variables:
        # Convert simple dict to Camunda variable format
        payload["variables"] = {
            name: {"value": value, "type": "String"} 
            for name, value in variables.items()
        }
    
    return await camunda_request(
        f"process-definition/key/{key}/start",
        method="POST",
        json_data=payload
    )


@mcp.tool()
async def list_process_instances(
    process_definition_key: Optional[str] = None,
    business_key: Optional[str] = None,
    active: bool = True,
    max_results: int = 50
) -> List[Dict]:
    """
    List process instances.
    
    Args:
        process_definition_key: Filter by process definition key
        business_key: Filter by business key
        active: Only return active instances (default: True)
        max_results: Maximum number of results to return
    
    Returns:
        List of process instances
    """
    params = {"maxResults": max_results}
    
    if process_definition_key:
        params["processDefinitionKey"] = process_definition_key
    if business_key:
        params["businessKey"] = business_key
    if active:
        params["active"] = "true"
    
    return await camunda_request("process-instance", params=params)


@mcp.tool()
async def get_process_instance(instance_id: str) -> Dict:
    """
    Get details of a specific process instance.
    
    Args:
        instance_id: The ID of the process instance
    
    Returns:
        Process instance details
    """
    return await camunda_request(f"process-instance/{instance_id}")


@mcp.tool()
async def delete_process_instance(
    instance_id: str,
    reason: Optional[str] = None
) -> str:
    """
    Delete (cancel) a process instance.
    
    Args:
        instance_id: The ID of the process instance to delete
        reason: Optional reason for deletion
    
    Returns:
        Success message
    """
    params = {}
    if reason:
        params["reason"] = reason
    
    await camunda_request(
        f"process-instance/{instance_id}",
        method="DELETE",
        params=params
    )
    return f"Process instance {instance_id} deleted successfully"


@mcp.tool()
async def list_tasks(
    process_instance_id: Optional[str] = None,
    assignee: Optional[str] = None,
    candidate_user: Optional[str] = None,
    max_results: int = 50
) -> List[Dict]:
    """
    List user tasks.
    
    Args:
        process_instance_id: Filter by process instance ID
        assignee: Filter by assigned user
        candidate_user: Filter by candidate user
        max_results: Maximum number of results to return
    
    Returns:
        List of tasks
    """
    params = {"maxResults": max_results}
    
    if process_instance_id:
        params["processInstanceId"] = process_instance_id
    if assignee:
        params["assignee"] = assignee
    if candidate_user:
        params["candidateUser"] = candidate_user
    
    return await camunda_request("task", params=params)


@mcp.tool()
async def get_task(task_id: str) -> Dict:
    """
    Get details of a specific task.
    
    Args:
        task_id: The ID of the task
    
    Returns:
        Task details
    """
    return await camunda_request(f"task/{task_id}")


@mcp.tool()
async def complete_task(
    task_id: str,
    variables: Optional[Dict[str, Any]] = None
) -> str:
    """
    Complete a user task.
    
    Args:
        task_id: The ID of the task to complete
        variables: Optional variables to submit with task completion
    
    Returns:
        Success message
    """
    payload = {}
    
    if variables:
        payload["variables"] = {
            name: {"value": value, "type": "String"} 
            for name, value in variables.items()
        }
    
    await camunda_request(
        f"task/{task_id}/complete",
        method="POST",
        json_data=payload
    )
    return f"Task {task_id} completed successfully"


@mcp.tool()
async def claim_task(task_id: str, user_id: str) -> str:
    """
    Claim a task for a specific user.
    
    Args:
        task_id: The ID of the task to claim
        user_id: The ID of the user claiming the task
    
    Returns:
        Success message
    """
    await camunda_request(
        f"task/{task_id}/claim",
        method="POST",
        json_data={"userId": user_id}
    )
    return f"Task {task_id} claimed by {user_id}"


@mcp.tool()
async def get_task_variables(task_id: str) -> Dict:
    """
    Get all variables for a specific task.
    
    Args:
        task_id: The ID of the task
    
    Returns:
        Dictionary of task variables
    """
    return await camunda_request(f"task/{task_id}/variables")


@mcp.tool()
async def get_process_variables(instance_id: str) -> Dict:
    """
    Get all variables for a process instance.
    
    Args:
        instance_id: The ID of the process instance
    
    Returns:
        Dictionary of process variables
    """
    return await camunda_request(f"process-instance/{instance_id}/variables")


@mcp.tool()
async def deploy_bpmn(
    deployment_name: str,
    bpmn_file_path: str
) -> Dict:
    """
    Deploy a BPMN file to Camunda.
    
    Args:
        deployment_name: Name for the deployment
        bpmn_file_path: Path to the BPMN file
    
    Returns:
        Deployment details
    """
    import aiofiles
    
    async with aiofiles.open(bpmn_file_path, 'rb') as f:
        content = await f.read()
    
    files = {
        'data': (os.path.basename(bpmn_file_path), content, 'application/xml')
    }
    
    url = f"{CAMUNDA_URL}/deployment/create"
    auth = get_auth()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            auth=auth,
            files=files,
            data={'deployment-name': deployment_name},
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    # Run the MCP server in HTTP SSE mode
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000, path="/mcp")
