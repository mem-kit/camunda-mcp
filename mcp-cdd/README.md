# StateStreet CDD Service (MCP)

This is a minimal simulated StateStreet Customer Due Diligence (CDD) MCP service.

Features
- Four simulated tools (MCP endpoints):
  - `get_customer_profile(customer_id)` — CustomerProfileService 统一客户档案读写
  - `get_risk_score(customer_id)` — RiskScoringService 多因子风险模型
  - `explain_risk(customer_id)` — Explain key contributors of the risk score
  - `generate_compliance_report(customer_id)` — Create a simulated compliance report

Running

Install the Python dependencies (recommended inside a virtual environment):

```powershell
python -m pip install -r requirements.txt
```

Start the service (it runs on port 3000):

```powershell
python "state_street_cdd.py"
```

The MCP endpoint is available at http://localhost:3000/mcp (Streamable HTTP transport for SSE).

Notes
- This service simulates outputs; replace the mocked logic for real integrations.

Example client

A minimal example client is included at `example_client.py` that demonstrates calling the four MCP tools directly by importing them (useful for local testing or unit tests).

Run the example client (when in the `mcp-cdd` folder):

```powershell
python example_client.py
```

The script will print the simulated customer profile, risk score, explanation and a compliance report to STDOUT.

Troubleshooting
- If you import functions decorated with `@mcp.tool()` you may end up with wrapper objects (not directly callable). The included `example_client.py` handles this and will try several ways to call the underlying function. If you still have an error, ensure you have the required dependencies installed and run the service modules directly.

Comprehensive scenario tests

The `example_client.py` now includes a simple comprehensive test that simulates two scenarios for each tool: a "positive" (low risk) and a "negative" (high risk) scenario with different recommendations and next steps. The script runs the base demo and then the scenario test when executed directly:

```powershell
python example_client.py
```

The output shows clearly separated POSITIVE and NEGATIVE scenario responses for each tool.

Server-side scenario support

Each MCP tool in `state_street_cdd.py` infers the scenario from the supplied `customer_id` string. You don't need to pass a separate `scenario` argument — instead use customer IDs that indicate scenario intent.

Rules the server uses (case-insensitive):
- If `customer_id` contains "neg" or "negative" → negative scenario
- If `customer_id` contains "pos" or "positive" → positive scenario
- Otherwise defaults to positive

Examples (local import & direct calls):

```py
# positive scenario via customer id
profile = await get_customer_profile("CUST-123-POS")

# negative scenario via customer id
profile = await get_customer_profile("CUST-456-NEG")
```

If you call the server from a remote client, include the same customer_id values in your request payload to select the desired scenario.

Chaining / next_steps

Tools now return structured `next_steps`. These can be simple instructions for humans (strings) or a tool descriptor with the fields:

- `tool`: tool name (e.g. `get_risk_score`)
- `params`: parameters (e.g. `{ "customer_id": "CUST-123-POS" }`)

Clients can follow these descriptors to chain calls automatically. The included `example_client.py` demonstrates a `follow_next_steps` helper that executes any tool calls returned in `next_steps` and forwards `customer_id` where not provided explicitly.
