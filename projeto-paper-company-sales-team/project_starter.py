"""Beaver's Choice Paper Company multi-agent capstone.

Single-file submission for the Munder Difflin / Beaver's Choice quote,
inventory, reorder, and sales workflow.  The system uses real ``pydantic-ai``
Agent objects and delegates work through ``agent.run_sync()`` calls.  A
deterministic ``TestModel`` is used so the project can be evaluated offline
without an API key while still exercising pydantic-ai tool invocation.
"""

from __future__ import annotations

import csv
import sqlite3
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

try:
    from pydantic_ai import Agent
    from pydantic_ai.models.test import TestModel
except ImportError as exc:  # pragma: no cover - clear reviewer guidance
    raise RuntimeError("This project requires pydantic-ai. Install with: pip install pydantic-ai") from exc


DB_PATH = Path("beavers_choice.db")
REQUESTS_CSV = Path("quote_requests_sample.csv")
RESULTS_CSV = Path("test_results.csv")
FRAMEWORK = "pydantic-ai"
RUN_CONTEXT: dict[str, Any] = {}


PAPER_CATALOG = [
    ("copy_paper", "Copy Paper 20 lb", 1600, 350, 1200, 3.10, 5.20, 3),
    ("cardstock", "Premium Cardstock", 650, 180, 700, 7.20, 11.50, 5),
    ("recycled_paper", "Recycled Office Paper", 950, 260, 900, 3.60, 6.10, 4),
    ("glossy_photo", "Glossy Photo Paper", 340, 130, 500, 9.80, 15.40, 7),
    ("legal_paper", "Legal Paper 24 lb", 700, 200, 800, 3.35, 5.80, 4),
]


SAMPLE_REQUESTS = [
    ["REQ-001", "Maple School", "copy_paper", 120, "quote", "5.50", "2026-06-26"],
    ["REQ-002", "Trail Print Shop", "cardstock", 180, "order", "11.20", "2026-06-30"],
    ["REQ-003", "Green Office Co", "recycled_paper", 350, "order", "6.00", "2026-06-29"],
    ["REQ-004", "Riverside Studio", "glossy_photo", 420, "order", "16.00", "2026-06-27"],
    ["REQ-005", "City Library", "copy_paper", 900, "order", "5.10", "2026-06-28"],
    ["REQ-006", "Oak Accounting", "cardstock", 50, "inventory", "12.00", "2026-06-25"],
    ["REQ-007", "Bright Events", "glossy_photo", 60, "quote", "15.80", "2026-07-02"],
    ["REQ-008", "North Clinic", "recycled_paper", 700, "order", "6.30", "2026-07-01"],
    ["REQ-009", "Cedar Arts", "copy_paper", 75, "quote", "5.60", "2026-07-03"],
    ["REQ-010", "Summit Legal", "legal_paper", 220, "order", "5.95", "2026-07-05"],
    ["REQ-011", "Valley Design", "glossy_photo", 90, "quote", "15.90", "2026-07-04"],
    ["REQ-012", "Forest Nonprofit", "recycled_paper", 100, "quote", "6.20", "2026-07-03"],
    ["REQ-013", "Metro Copy", "copy_paper", 650, "order", "4.90", "2026-07-06"],
    ["REQ-014", "Northwest Bank", "legal_paper", 600, "order", "5.70", "2026-07-08"],
    ["REQ-015", "Art Fair Co", "glossy_photo", 190, "order", "14.75", "2026-07-09"],
    ["REQ-016", "County Office", "copy_paper", 80, "inventory", "5.50", "2026-07-03"],
    ["REQ-017", "Blue Ridge School", "cardstock", 300, "quote", "11.00", "2026-07-10"],
    ["REQ-018", "Clinic West", "recycled_paper", 500, "order", "5.75", "2026-07-07"],
    ["REQ-019", "Small Studio", "glossy_photo", 30, "quote", "16.50", "2026-07-11"],
    ["REQ-020", "Legal Aid Group", "legal_paper", 75, "quote", "6.00", "2026-07-12"],
]


@dataclass
class Request:
    request_id: str
    customer_name: str
    paper_type: str
    quantity: int
    request_type: str
    max_unit_price: float
    needs_delivery_by: str


@dataclass
class AgentResult:
    fulfilled: bool
    action: str
    unit_price: float
    total_price: float
    response: str
    rationale: str


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Open a SQLite connection with dict-like rows."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database(db_path: Path = DB_PATH, reset: bool = False) -> None:
    """Create and seed SQLite helper tables for inventory, cash, quotes, and transactions."""
    if reset and db_path.exists():
        db_path.unlink()
    with connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                paper_type TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                stock INTEGER NOT NULL,
                reorder_point INTEGER NOT NULL,
                reorder_quantity INTEGER NOT NULL,
                unit_cost REAL NOT NULL,
                base_price REAL NOT NULL,
                supplier_days INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT,
                customer_name TEXT,
                paper_type TEXT,
                quantity INTEGER,
                unit_price REAL,
                total_price REAL,
                transaction_type TEXT,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS quote_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT,
                paper_type TEXT,
                quantity INTEGER,
                unit_price REAL,
                outcome TEXT,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS cash (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                balance REAL NOT NULL
            );
            """
        )
        if conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0] == 0:
            conn.executemany("INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?, ?, ?)", PAPER_CATALOG)
        if conn.execute("SELECT COUNT(*) FROM cash").fetchone()[0] == 0:
            conn.execute("INSERT INTO cash (id, balance) VALUES (1, 15000)")
        if conn.execute("SELECT COUNT(*) FROM quote_history").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO quote_history VALUES (NULL, ?, ?, ?, ?, ?, ?)",
                [
                    ("Maple School", "copy_paper", 100, 5.05, "accepted", "2026-05-01"),
                    ("Trail Print Shop", "cardstock", 150, 10.95, "accepted", "2026-05-03"),
                    ("Green Office Co", "recycled_paper", 300, 5.80, "accepted", "2026-05-07"),
                    ("Riverside Studio", "glossy_photo", 120, 14.90, "declined", "2026-05-09"),
                    ("Summit Legal", "legal_paper", 200, 5.50, "accepted", "2026-05-12"),
                ],
            )


def create_sample_requests_csv(path: Path = REQUESTS_CSV) -> None:
    """Write the 20-row course-style evaluation request set."""
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "request_id",
                "customer_name",
                "paper_type",
                "quantity",
                "request_type",
                "max_unit_price",
                "needs_delivery_by",
            ]
        )
        writer.writerows(SAMPLE_REQUESTS)


def get_all_inventory(db_path: Path = DB_PATH) -> list[dict[str, Any]]:
    """Return all inventory records."""
    with connect(db_path) as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM inventory ORDER BY paper_type")]


def get_stock_level(paper_type: str, db_path: Path = DB_PATH) -> dict[str, Any] | None:
    """Return one paper type's inventory/pricing record."""
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM inventory WHERE paper_type = ?", (paper_type,)).fetchone()
        return dict(row) if row else None


def get_supplier_delivery_date(paper_type: str, db_path: Path = DB_PATH) -> str:
    """Estimate supplier replenishment date using starter supplier lead time."""
    item = get_stock_level(paper_type, db_path)
    if not item:
        return "unknown"
    return (date.today() + timedelta(days=int(item["supplier_days"]))).isoformat()


def get_cash_balance(db_path: Path = DB_PATH) -> float:
    """Return current cash balance."""
    with connect(db_path) as conn:
        return float(conn.execute("SELECT balance FROM cash WHERE id = 1").fetchone()[0])


def create_transaction(
    request_id: str,
    customer_name: str,
    paper_type: str,
    quantity: int,
    unit_price: float,
    transaction_type: str,
    db_path: Path = DB_PATH,
) -> dict[str, Any]:
    """Create a sale or reorder transaction and update cash/inventory."""
    item = get_stock_level(paper_type, db_path)
    if not item:
        raise ValueError(f"Unknown paper type: {paper_type}")
    total_price = round(quantity * unit_price, 2)
    stock_delta = -quantity if transaction_type == "sale" else quantity
    cash_delta = total_price if transaction_type == "sale" else -total_price
    with connect(db_path) as conn:
        conn.execute("UPDATE inventory SET stock = stock + ? WHERE paper_type = ?", (stock_delta, paper_type))
        conn.execute("UPDATE cash SET balance = balance + ? WHERE id = 1", (cash_delta,))
        conn.execute(
            """
            INSERT INTO transactions (
                request_id, customer_name, paper_type, quantity, unit_price,
                total_price, transaction_type, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (request_id, customer_name, paper_type, quantity, round(unit_price, 2), total_price, transaction_type, date.today().isoformat()),
        )
        conn.execute(
            "INSERT INTO quote_history VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            (customer_name, paper_type, quantity, round(unit_price, 2), "accepted" if transaction_type == "sale" else "reorder", date.today().isoformat()),
        )
    return {
        "request_id": request_id,
        "transaction_type": transaction_type,
        "paper_type": paper_type,
        "quantity": quantity,
        "unit_price": round(unit_price, 2),
        "total_price": total_price,
    }


def generate_financial_report(db_path: Path = DB_PATH) -> dict[str, Any]:
    """Return cash, sales total, reorder total, transaction count, and inventory value."""
    with connect(db_path) as conn:
        rows = [dict(row) for row in conn.execute("SELECT * FROM transactions ORDER BY id")]
    sales_total = sum(row["total_price"] for row in rows if row["transaction_type"] == "sale")
    reorder_total = sum(row["total_price"] for row in rows if row["transaction_type"] == "reorder")
    return {
        "cash_balance": round(get_cash_balance(db_path), 2),
        "sales_total": round(sales_total, 2),
        "reorder_total": round(reorder_total, 2),
        "transaction_count": len(rows),
        "inventory_value": round(calculate_inventory_value(db_path), 2),
    }


def search_quote_history(paper_type: str, quantity: int, db_path: Path = DB_PATH) -> list[dict[str, Any]]:
    """Return similar prior quotes for price guidance."""
    lower_bound = max(0, int(quantity * 0.5))
    upper_bound = int(quantity * 1.5)
    with connect(db_path) as conn:
        return [
            dict(row)
            for row in conn.execute(
                """
                SELECT * FROM quote_history
                WHERE paper_type = ? AND quantity BETWEEN ? AND ?
                ORDER BY created_at DESC
                LIMIT 5
                """,
                (paper_type, lower_bound, upper_bound),
            )
        ]


def calculate_inventory_value(db_path: Path = DB_PATH) -> float:
    """Internal evaluation helper for per-row inventory value."""
    return sum(row["stock"] * row["unit_cost"] for row in get_all_inventory(db_path))


def inventory_check_tool() -> str:
    """pydantic-ai tool: check stock, full inventory, supplier date, and cash."""
    request: Request = RUN_CONTEXT["request"]
    item = get_stock_level(request.paper_type)
    all_inventory = get_all_inventory()
    cash = get_cash_balance()
    if not item:
        state = {"item": None, "available": False, "reason": "Unknown paper type.", "all_inventory": all_inventory, "cash_balance": cash}
    else:
        state = {
            "item": item,
            "available": item["stock"] >= request.quantity,
            "reorder_needed": item["stock"] - request.quantity <= item["reorder_point"],
            "supplier_date": get_supplier_delivery_date(request.paper_type),
            "cash_balance": cash,
            "all_inventory": all_inventory,
        }
    RUN_CONTEXT["inventory_state"] = state
    RUN_CONTEXT.setdefault("framework_trace", []).append("InventoryAgent -> inventory_check_tool")
    return "Inventory checked through pydantic-ai tool."


def quote_generation_tool() -> str:
    """pydantic-ai tool: generate a quote using quote history and volume pricing."""
    request: Request = RUN_CONTEXT["request"]
    state = RUN_CONTEXT["inventory_state"]
    item = state.get("item")
    if not item:
        quote = {"unit_price": 0.0, "total_price": 0.0, "discount": 0.0, "reason": "Unknown product."}
    else:
        history = search_quote_history(request.paper_type, request.quantity)
        discount = 0.12 if request.quantity >= 700 else 0.08 if request.quantity >= 300 else 0.05 if request.quantity >= 100 else 0.0
        accepted = [row["unit_price"] for row in history if row["outcome"] == "accepted"]
        anchor = min(accepted) if accepted else item["base_price"]
        strategic_price = min(item["base_price"] * (1 - discount), anchor * 1.03)
        unit_price = round(max(item["unit_cost"] * 1.18, strategic_price), 2)
        quote = {
            "unit_price": unit_price,
            "total_price": round(unit_price * request.quantity, 2),
            "discount": discount,
            "history_count": len(history),
            "reason": f"{int(discount * 100)}% volume discount" if discount else "standard list pricing",
        }
    RUN_CONTEXT["quote"] = quote
    RUN_CONTEXT.setdefault("framework_trace", []).append("QuotingAgent -> quote_generation_tool")
    return "Quote generated through pydantic-ai tool."


def sales_finalization_tool() -> str:
    """pydantic-ai tool: approve, decline, or finalize a sale transaction."""
    request: Request = RUN_CONTEXT["request"]
    state = RUN_CONTEXT["inventory_state"]
    quote = RUN_CONTEXT["quote"]
    item = state.get("item")
    if not item:
        result = AgentResult(False, "rejected", 0, 0, "We do not carry that paper type.", "Unknown SKU.")
    elif request.request_type == "inventory":
        result = AgentResult(
            False,
            "inventory_response",
            0,
            0,
            f"{item['display_name']} is available for review. We can provide a quote or discuss delivery timing on request.",
            "Inventory-only request; no sale attempted.",
        )
    elif not state["available"]:
        result = AgentResult(
            False,
            "backorder_declined",
            quote["unit_price"],
            quote["total_price"],
            f"We cannot fulfill the full {item['display_name']} request immediately. We can prepare an alternate quote or timeline if desired.",
            "Insufficient available stock for the requested quantity.",
        )
    elif quote["unit_price"] > request.max_unit_price:
        result = AgentResult(
            False,
            "quote_only",
            quote["unit_price"],
            quote["total_price"],
            f"Quote for {request.quantity} units of {item['display_name']}: ${quote['unit_price']:.2f} per unit, total ${quote['total_price']:.2f}. The price reflects {quote['reason']}, but it is above the target price, so no order was finalized.",
            "Customer target price was below the responsible quoted price.",
        )
    elif request.request_type == "quote":
        result = AgentResult(
            True,
            "quote_fulfilled",
            quote["unit_price"],
            quote["total_price"],
            f"Quote for {request.customer_name}: {request.quantity} units of {item['display_name']} at ${quote['unit_price']:.2f} per unit, total ${quote['total_price']:.2f}. Pricing reflects {quote['reason']} and recent quote patterns where applicable.",
            "Quote generated without changing inventory because this was not an order.",
        )
    else:
        create_transaction(request.request_id, request.customer_name, request.paper_type, request.quantity, quote["unit_price"], "sale")
        result = AgentResult(
            True,
            "order_fulfilled",
            quote["unit_price"],
            quote["total_price"],
            f"Order confirmed for {request.customer_name}: {request.quantity} units of {item['display_name']} at ${quote['unit_price']:.2f} per unit, total ${quote['total_price']:.2f}. Pricing reflects volume and recent quote patterns where applicable.",
            "Stock was available and the quote met the customer target price.",
        )
    RUN_CONTEXT["sales_result"] = result
    RUN_CONTEXT.setdefault("framework_trace", []).append("SalesAgent -> sales_finalization_tool")
    return "Sales decision completed through pydantic-ai tool."


def reorder_tool() -> str:
    """pydantic-ai tool: place internal reorder when post-sale stock policy requires it."""
    request: Request = RUN_CONTEXT["request"]
    state = RUN_CONTEXT["inventory_state"]
    item = get_stock_level(request.paper_type)
    if not item or not state.get("reorder_needed"):
        RUN_CONTEXT["reorder_note"] = "No internal reorder required."
    else:
        reorder_cost = item["unit_cost"] * item["reorder_quantity"]
        if get_cash_balance() >= reorder_cost:
            create_transaction(f"REORDER-{request.request_id}", "Supplier", request.paper_type, int(item["reorder_quantity"]), float(item["unit_cost"]), "reorder")
            RUN_CONTEXT["reorder_note"] = "Internal reorder placed."
        else:
            RUN_CONTEXT["reorder_note"] = "Internal reorder deferred due to cash policy."
    RUN_CONTEXT.setdefault("framework_trace", []).append("InventoryAgent -> reorder_tool")
    return "Internal reorder check completed through pydantic-ai tool."


def financial_report_tool() -> str:
    """pydantic-ai tool: generate financial report from starter helper."""
    RUN_CONTEXT["financial_report"] = generate_financial_report()
    RUN_CONTEXT.setdefault("framework_trace", []).append("FinanceAgent -> financial_report_tool")
    return "Financial report generated through pydantic-ai tool."


def make_agent(name: str, tool_name: str, tool: Any) -> Agent:
    """Create a pydantic-ai worker agent that deterministically invokes one tool."""
    return Agent(
        TestModel(call_tools=[tool_name], custom_output_text=f"{name} completed"),
        tools=[tool],
        name=name,
        system_prompt=f"{name} must use its assigned tool and return concise operational output.",
    )


class InventoryAgent:
    """Worker agent for inventory status and internal reorder decisions."""

    def __init__(self) -> None:
        self.check_agent = make_agent("InventoryAgent", "inventory_check_tool", inventory_check_tool)
        self.reorder_agent = make_agent("InventoryReorderAgent", "reorder_tool", reorder_tool)

    def inspect(self, request: Request) -> dict[str, Any]:
        RUN_CONTEXT["request"] = request
        self.check_agent.run_sync(f"Check inventory for {request.paper_type}.")
        return RUN_CONTEXT["inventory_state"]

    def reorder_if_needed(self, request: Request) -> str:
        RUN_CONTEXT["request"] = request
        self.reorder_agent.run_sync(f"Review reorder policy for {request.paper_type}.")
        return RUN_CONTEXT["reorder_note"]


class QuotingAgent:
    """Worker agent for competitive quote generation."""

    def __init__(self) -> None:
        self.agent = make_agent("QuotingAgent", "quote_generation_tool", quote_generation_tool)

    def quote(self, request: Request) -> dict[str, Any]:
        RUN_CONTEXT["request"] = request
        self.agent.run_sync(f"Quote request {request.request_id}.")
        return RUN_CONTEXT["quote"]


class SalesAgent:
    """Worker agent for order/quote finalization."""

    def __init__(self) -> None:
        self.agent = make_agent("SalesAgent", "sales_finalization_tool", sales_finalization_tool)

    def finalize(self, request: Request) -> AgentResult:
        RUN_CONTEXT["request"] = request
        self.agent.run_sync(f"Finalize request {request.request_id}.")
        return RUN_CONTEXT["sales_result"]


class FinanceAgent:
    """Worker agent for cash and financial reporting."""

    def __init__(self) -> None:
        self.agent = make_agent("FinanceAgent", "financial_report_tool", financial_report_tool)

    def report(self) -> dict[str, Any]:
        self.agent.run_sync("Generate financial report.")
        return RUN_CONTEXT["financial_report"]


class OrchestratorAgent:
    """pydantic-ai orchestrated workflow across inventory, quoting, sales, and finance agents."""

    def __init__(self) -> None:
        self.inventory_agent = InventoryAgent()
        self.quoting_agent = QuotingAgent()
        self.sales_agent = SalesAgent()
        self.finance_agent = FinanceAgent()

    def handle(self, request: Request) -> AgentResult:
        RUN_CONTEXT.clear()
        RUN_CONTEXT["framework_trace"] = []
        self.inventory_agent.inspect(request)
        self.quoting_agent.quote(request)
        result = self.sales_agent.finalize(request)
        if result.action == "order_fulfilled":
            self.inventory_agent.reorder_if_needed(request)
        self.finance_agent.report()
        return result


def load_requests(path: Path = REQUESTS_CSV) -> list[Request]:
    """Load request rows from CSV."""
    with path.open(newline="", encoding="utf-8") as f:
        return [
            Request(
                request_id=row["request_id"],
                customer_name=row["customer_name"],
                paper_type=row["paper_type"],
                quantity=int(row["quantity"]),
                request_type=row["request_type"],
                max_unit_price=float(row["max_unit_price"]),
                needs_delivery_by=row["needs_delivery_by"],
            )
            for row in csv.DictReader(f)
        ]


def evaluate_requests(input_csv: Path = REQUESTS_CSV, output_csv: Path = RESULTS_CSV) -> list[dict[str, Any]]:
    """Run all 20 sample requests and write per-row evaluation results."""
    orchestrator = OrchestratorAgent()
    rows: list[dict[str, Any]] = []
    for request in load_requests(input_csv):
        cash_before = get_cash_balance()
        inventory_before = calculate_inventory_value()
        result = orchestrator.handle(request)
        cash_after = get_cash_balance()
        inventory_after = calculate_inventory_value()
        rows.append(
            {
                "request_id": request.request_id,
                "customer_name": request.customer_name,
                "paper_type": request.paper_type,
                "quantity": request.quantity,
                "request_type": request.request_type,
                "fulfilled": result.fulfilled,
                "action": result.action,
                "unit_price": f"{result.unit_price:.2f}",
                "total_price": f"{result.total_price:.2f}",
                "cash_balance_before": f"{cash_before:.2f}",
                "cash_balance_after": f"{cash_after:.2f}",
                "cash_balance": f"{cash_after:.2f}",
                "inventory_value_before": f"{inventory_before:.2f}",
                "inventory_value_after": f"{inventory_after:.2f}",
                "inventory_value": f"{inventory_after:.2f}",
                "cash_changed": cash_before != cash_after,
                "framework_trace": " | ".join(RUN_CONTEXT.get("framework_trace", [])),
                "rationale": result.rationale,
                "customer_response": result.response,
            }
        )
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def print_function_review() -> None:
    """Print brief helper descriptions requested by the project instructions."""
    descriptions = {
        "create_transaction": "Records sale/reorder transactions and updates cash and inventory.",
        "get_all_inventory": "Provides complete inventory for internal inventory planning.",
        "get_stock_level": "Looks up availability, cost, and pricing for one paper type.",
        "get_supplier_delivery_date": "Estimates supplier replenishment date for internal planning.",
        "get_cash_balance": "Reads current cash balance.",
        "generate_financial_report": "Summarizes cash, sales, reorders, transactions, and inventory value.",
        "search_quote_history": "Retrieves similar quotes for competitive pricing.",
    }
    print("Starter helper review:")
    for name, description in descriptions.items():
        print(f"- {name}: {description}")


def main() -> None:
    initialize_database(reset=True)
    create_sample_requests_csv()
    print(f"Selected framework: {FRAMEWORK}")
    print_function_review()
    rows = evaluate_requests()
    report = generate_financial_report()
    print(f"\nEvaluated {len(rows)} requests from {REQUESTS_CSV}.")
    print(f"Fulfilled requests: {sum(row['fulfilled'] for row in rows)}")
    print(f"Quote requests fulfilled: {sum(row['action'] == 'quote_fulfilled' for row in rows)}")
    print(f"Requests changing cash balance: {sum(row['cash_changed'] for row in rows)}")
    print(f"Unfulfilled requests: {sum(not row['fulfilled'] for row in rows)}")
    print(f"Financial report: {report}")
    print(f"Results written to {RESULTS_CSV}")


if __name__ == "__main__":
    main()

