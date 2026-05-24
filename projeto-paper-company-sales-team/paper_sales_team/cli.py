from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import SalesOpportunity
from .orchestrator import PaperSalesTeam
from .renderer import render_markdown


def load_opportunity(path: Path) -> SalesOpportunity:
    data = json.loads(path.read_text(encoding="utf-8"))
    return SalesOpportunity(
        company_name=data["company_name"],
        segment=data["segment"],
        monthly_volume_units=int(data["monthly_volume_units"]),
        sustainability_need=data["sustainability_need"],
        budget=float(data["budget"]),
        urgency=data["urgency"],
        stage=data.get("stage", "new"),
        notes=data.get("notes", ""),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Paper Company Sales Team workflow")
    parser.add_argument("opportunity_json", type=Path, help="Path to sales opportunity JSON")
    parser.add_argument("--output", type=Path, help="Optional Markdown output path")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    opportunity = load_opportunity(args.opportunity_json)
    plan = PaperSalesTeam().run(opportunity)
    markdown = render_markdown(plan)

    if args.output:
        args.output.write_text(markdown, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(markdown)


if __name__ == "__main__":
    main()
