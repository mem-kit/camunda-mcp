
import asyncio
import json
import inspect
from typing import Any

# Example client that calls the async tools directly by importing them
# This file demonstrates how to interact with the simulated MCP tools in
# `state_street_cdd.py` when running locally (same process / module path).

from state_street_cdd import (
    get_customer_profile,
    get_risk_score,
    explain_risk,
    generate_compliance_report,
)


async def _call_tool(tool: Any, *args, **kwargs):
    """Call a tool that may be wrapped by FastMCP.

    FastMCP's @mcp.tool decorator wraps the original function into a helper
    object (e.g. FunctionTool). This helper tries multiple strategies to
    detect and call the original function: __wrapped__, func, fn, or
    callable attributes like call/invoke. It supports both sync and async
    underlying functions.
    """
    # 1) If the tool is a callable coroutine function or returns awaitable, just call
    try:
        if callable(tool):
            res = tool(*args, **kwargs)
            if inspect.isawaitable(res):
                return await res
            return res
    except TypeError:
        # Not callable (common for FunctionTool wrappers), fall through to other attempts
        pass

    # 2) Look for common attributes that store the original function
    for attr in ("__wrapped__", "func", "fn", "function"):
        if hasattr(tool, attr):
            orig = getattr(tool, attr)
            if callable(orig):
                res = orig(*args, **kwargs)
                if inspect.isawaitable(res):
                    return await res
                return res

    # 3) Look for invocation helpers like .call(), .invoke(), or .run()
    for method in ("call", "invoke", "run"):
        if hasattr(tool, method) and callable(getattr(tool, method)):
            res = getattr(tool, method)(*args, **kwargs)
            if inspect.isawaitable(res):
                return await res
            return res

    # 4) If we got this far, provide a helpful error
    raise TypeError(f"Tool object of type {type(tool)!r} is not callable and no underlying function was found")


async def run_demo(customer_id: str = "CUST-12345"):
    # Call the simulated MCP tools via the robust helper above
    profile = await _call_tool(get_customer_profile, customer_id)
    score = await _call_tool(get_risk_score, customer_id)
    explanation = await _call_tool(explain_risk, customer_id)
    report = await _call_tool(generate_compliance_report, customer_id)

    print("\n--- Example client results (local import) ---\n")
    print("Customer profile:\n", json.dumps(profile, indent=2, ensure_ascii=False))
    print("\nRisk score:\n", json.dumps(score, indent=2, ensure_ascii=False))
    print("\nRisk explanation:\n", json.dumps(explanation, indent=2, ensure_ascii=False))
    print("\nCompliance report:\n", json.dumps(report, indent=2, ensure_ascii=False))
    # Follow next_steps returned by the profile to exercise server-side chaining
    await follow_next_steps(profile)


async def follow_next_steps(result: dict, max_depth: int = 4, _depth: int = 0):
    """Follow structured next_steps from a tool result and invoke any referenced tools.

    Each next_step can be:
    - a string (human action) -> printed and ignored for chaining
    - a dict with 'tool' (name) and optional 'params' dict -> client will call the corresponding tool

    This helper prevents infinite loops using max_depth.
    """
    if _depth >= max_depth:
        print(f"Max next-step depth {_depth} reached, stopping further chaining.")
        return

    steps = result.get("next_steps") or []
    if not steps:
        return

    tool_map = {
        "get_customer_profile": get_customer_profile,
        "get_risk_score": get_risk_score,
        "explain_risk": explain_risk,
        "generate_compliance_report": generate_compliance_report,
    }

    for step in steps:
        if isinstance(step, dict) and step.get("tool"):
            tool_name = step["tool"]
            params = step.get("params", {})
            # if customer_id not provided in params, use parent's customer_id when available
            if "customer_id" not in params and "customer_id" in result:
                params["customer_id"] = result["customer_id"]

            func = tool_map.get(tool_name)
            if not func:
                print(f"Unknown tool referenced in next_steps: {tool_name}")
                continue

            print(f"\n-- Following next_step: calling {tool_name} with params={params} (depth {_depth+1})")
            try:
                resp = await _call_tool(func, **params)
                print(f"Result from {tool_name}:", json.dumps(resp, indent=2, ensure_ascii=False))
                # recursively follow next steps
                await follow_next_steps(resp, max_depth=max_depth, _depth=_depth + 1)
            except Exception as e:
                print(f"Error when calling {tool_name}: {e}")

        else:
            # plain string next-step, print for human ops
            print(f"Next action (human): {step}")


# The example client now calls server-side scenarios directly; local transform helpers removed


async def run_scenarios(customer_id: str = "CUST-12345"):
    """Run positive and negative scenario simulations for each tool and print outputs."""
    # call the base tools
    profile = await _call_tool(get_customer_profile, customer_id)
    score = await _call_tool(get_risk_score, customer_id)
    explanation = await _call_tool(explain_risk, customer_id)
    report = await _call_tool(generate_compliance_report, customer_id)

    # Query the tools for both *server-side* scenarios so we validate server behavior
    # Use different customer IDs to indicate scenario. No explicit scenario parameter required.
    pos_customer = f"{customer_id}-POS"
    neg_customer = f"{customer_id}-NEG"

    pos_profile = await _call_tool(get_customer_profile, pos_customer)
    pos_score = await _call_tool(get_risk_score, pos_customer)
    pos_expl = await _call_tool(explain_risk, pos_customer)
    pos_report = await _call_tool(generate_compliance_report, pos_customer)

    neg_profile = await _call_tool(get_customer_profile, neg_customer)
    neg_score = await _call_tool(get_risk_score, neg_customer)
    neg_expl = await _call_tool(explain_risk, neg_customer)
    neg_report = await _call_tool(generate_compliance_report, neg_customer)

    print("\n================== POSITIVE SCENARIO ==================")
    print("Customer profile:\n", json.dumps(pos_profile, indent=2, ensure_ascii=False))
    print("\nRisk score:\n", json.dumps(pos_score, indent=2, ensure_ascii=False))
    print("\nRisk explanation:\n", json.dumps(pos_expl, indent=2, ensure_ascii=False))
    print("\nCompliance report:\n", json.dumps(pos_report, indent=2, ensure_ascii=False))
    # follow chain from profile for the positive scenario
    await follow_next_steps(pos_profile)

    print("\n================== NEGATIVE SCENARIO ==================")
    print("Customer profile:\n", json.dumps(neg_profile, indent=2, ensure_ascii=False))
    print("\nRisk score:\n", json.dumps(neg_score, indent=2, ensure_ascii=False))
    print("\nRisk explanation:\n", json.dumps(neg_expl, indent=2, ensure_ascii=False))
    print("\nCompliance report:\n", json.dumps(neg_report, indent=2, ensure_ascii=False))
    # follow chain from profile for the negative scenario
    await follow_next_steps(neg_profile)


if __name__ == "__main__":
    # Run the demo client using asyncio event loop
    # Run the demo client then run the comprehensive positive/negative scenario test
    asyncio.run(run_demo())
    print('\n\n***** Now running comprehensive positive/negative scenario tests *****\n')
    asyncio.run(run_scenarios())
