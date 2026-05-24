from __future__ import annotations

import argparse

from .models import ClimatePreference, Pace, TravelRequest, TravelStyle
from .orchestrator import TripPlanner
from .renderer import render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AgentsVille multi-agent trip planner")
    parser.add_argument("--origin", required=True, help="Cidade de origem")
    parser.add_argument("--days", type=int, required=True, help="Duracao da viagem em dias")
    parser.add_argument("--budget", type=float, required=True, help="Orcamento total disponivel")
    parser.add_argument("--style", choices=["culture", "adventure", "relax", "food", "family"], default="culture")
    parser.add_argument("--climate", choices=["warm", "mild", "cold", "any"], default="any")
    parser.add_argument("--pace", choices=["slow", "balanced", "packed"], default="balanced")
    parser.add_argument("--travelers", type=int, default=1)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    request = TravelRequest(
        origin=args.origin,
        days=args.days,
        budget=args.budget,
        style=args.style,
        climate=args.climate,
        pace=args.pace,
        travelers=args.travelers,
    )
    plan = TripPlanner().plan(request)
    print(render_markdown(plan))


if __name__ == "__main__":
    main()
