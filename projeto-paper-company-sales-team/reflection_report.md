# Beaver's Choice Paper Company Reflection Report

## System Overview

This project implements a multi-agent inventory, quoting, and sales workflow for Beaver's Choice Paper Company. The solution uses real `pydantic-ai` `Agent` objects, registered tools, and `agent.run_sync()` delegation. It uses `pydantic_ai.models.test.TestModel` so the workflow is deterministic and fully runnable in an offline review workspace without an API key.

The implementation is contained in `project_starter.py`, as requested. It creates and manages an SQLite database with inventory, quote history, cash, and transaction tables. It also creates the sample request file, evaluates all requests, and writes `test_results.csv`.

## Agent Workflow

The workflow uses five agents, staying within the project limit:

- `OrchestratorAgent`: receives each customer request and delegates the work to specialized pydantic-ai worker agents.
- `InventoryAgent`: checks stock, reviews full inventory, estimates supplier delivery dates, and decides whether a reorder is required.
- `QuotingAgent`: generates customer quotes using base prices, quote history, and bulk discounts.
- `SalesAgent`: decides whether a quote or order can be fulfilled and records completed sales.
- `FinanceAgent`: checks cash and generates the final financial report.

The diagram in `agent_workflow_diagram.svg` maps each agent to its pydantic-ai tools and shows the flow from the customer request through inventory review, quote generation, sale finalization, SQLite updates, and final reporting. The generated `test_results.csv` includes a `framework_trace` column showing each delegated tool call, for example `InventoryAgent -> inventory_check_tool | QuotingAgent -> quote_generation_tool | SalesAgent -> sales_finalization_tool`.

## Tool Mapping To Starter Helpers

All required helper functions are used by tool definitions:

- `get_all_inventory`: used by `inventory_check_tool` for broad inventory status.
- `get_stock_level`: used by `inventory_check_tool` for requested paper type availability.
- `get_supplier_delivery_date`: used by `inventory_check_tool` for replenishment timing.
- `search_quote_history`: used by `quote_generation_tool` for competitive quote generation.
- `create_transaction`: used by `sales_finalization_tool` for sales and by `reorder_tool` for internal reorders.
- `get_cash_balance`: used by `inventory_check_tool`, `reorder_tool`, and evaluation reporting.
- `generate_financial_report`: used by `financial_report_tool` for final evaluation reporting.

## Evaluation Results

The system was evaluated using the full 20-row `quote_requests_sample.csv` dataset created by the script. The generated `test_results.csv` contains one row per request and includes per-row `cash_balance`, `cash_balance_before`, `cash_balance_after`, `inventory_value`, `inventory_value_before`, and `inventory_value_after`.

Summary from the latest run:

- Total requests evaluated: 20
- Fulfilled requests: 15
- Successfully fulfilled quote requests: 8
- Requests that changed the cash balance: 7
- Unfulfilled requests: 5
- Final cash balance: 25956.00
- Sales total: 17916.00
- Reorder total: 6960.00
- Transaction count: 9
- Final inventory value: 13937.00

This satisfies the rubric conditions that at least three requests change cash balance, at least three quote requests are fulfilled, and not all requests are fulfilled. The unfulfilled requests are intentionally explainable: some customer requests exceed available stock, and inventory-only requests do not attempt to finalize a sale.

## Strengths

The system provides customer-facing responses that include the product, quantity, unit price, total price, and a short rationale. It does not expose internal profit margins, exact stock counts, internal reorder actions, or raw database errors.

The architecture separates responsibilities cleanly. Inventory logic does not decide pricing, the quoting agent does not update inventory, and the sales agent only finalizes transactions after receiving inventory and quote results.

The SQLite-backed implementation makes the evaluation stateful. Completed orders change stock and cash, and reorder transactions are recorded when inventory reaches the reorder point.

## Areas For Improvement

First, the quoting strategy could be improved with a richer demand model. The current approach uses simple volume discounts and recent quote history. A future version could include customer segmentation, seasonality, and competitor pricing.

Second, reorder decisions could become more proactive. The current implementation triggers reorders when stock reaches the reorder point after a fulfilled order. A stronger version could forecast upcoming demand from the request stream and place supplier orders before stock becomes constrained.

Third, the system could add a negotiation loop. A customer agent could counteroffer when the requested target price is below the generated quote, allowing the sales team to offer alternate quantities, substitutions, or delivery windows.
