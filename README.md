# Camunda MCP Server
Camunda MCP server using FastMCP. It is a Python based MCP server that connects to your Camunda instance.


## Setup

you can set the connection information in the .env

```
camunda_url=http://192.168.50.156:8080/engine-rest
camunda_user=demo
camunda_password=demo
```

Then using Camunda docker to run it in local: 

```
docker pull camunda/camunda-bpm-platform:latest

docker run -d --name camunda -p 8080:8080 camunda/camunda-bpm-platform:latest
```

### Test URL:

http://localhost:8080/engine-rest/process-definition

http://localhost:8080/engine-rest/task

The full REST API document is here: https://docs.camunda.org/rest/camunda-bpm-platform/7.24/#tag/Process-Definition


### Run

```
cd mcp-server
pip install -r requirements.txt
python camunda_server.py
```

### Test MCP

mcp.json

```

{

    "servers": {
        "camunda": {
            "type": "http",
            "url": "http://127.0.0.1:8000/mcp"        
        }
    }
}


```




