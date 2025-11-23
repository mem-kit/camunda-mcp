# Camunda MCP Server

A Model Context Protocol (MCP) server for interacting with Camunda BPM Platform, built with FastMCP.

## Features

This MCP server provides tools to:
- List and get process definitions
- Start and manage process instances
- List, claim, and complete user tasks
- Get process and task variables
- Deploy BPMN files

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure the server by editing `.env`:
```
CAMUNDA_URL=http://192.168.50.156:8080/engine-rest
CAMUNDA_USER=demo
CAMUNDA_PASSWORD=demo
```

3. Run the server:
```bash
python camunda_server.py
```

Or use with mcp CLI:
```bash
mcp install camunda_server.py
```

## Available Tools

### Process Definitions
- `list_process_definitions` - List all process definitions
- `get_process_definition` - Get details of a specific process definition

### Process Instances
- `start_process_instance` - Start a new process instance
- `list_process_instances` - List process instances
- `get_process_instance` - Get details of a specific instance
- `delete_process_instance` - Delete (cancel) a process instance

### Tasks
- `list_tasks` - List user tasks
- `get_task` - Get details of a specific task
- `complete_task` - Complete a user task
- `claim_task` - Claim a task for a user

### Variables
- `get_task_variables` - Get variables for a task
- `get_process_variables` - Get variables for a process instance

### Deployment
- `deploy_bpmn` - Deploy a BPMN file to Camunda

## Usage with Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "camunda": {
      "command": "python",
      "args": ["/Users/meadlai/git/cosmos-will/workflow-engine/mcp-server/camunda_server.py"],
      "env": {
        "CAMUNDA_URL": "http://192.168.50.156:8080/engine-rest",
        "CAMUNDA_USER": "demo",
        "CAMUNDA_PASSWORD": "demo"
      }
    }
  }
}
```

## Example Queries

- "List all process definitions"
- "Start a process instance with key 'invoice-process'"
- "Show me all active tasks"
- "Complete task with ID xyz"
- "Get variables for process instance abc"
