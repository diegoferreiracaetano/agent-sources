from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import Project, TeamMember, WorkItem
from .orchestrator import AgenticProjectManager
from .renderer import render_markdown


def load_project(path: Path) -> Project:
    data = json.loads(path.read_text(encoding="utf-8"))
    team = tuple(
        TeamMember(
            name=member["name"],
            skills=tuple(member.get("skills", [])),
            capacity=int(member["capacity"]),
        )
        for member in data["team"]
    )
    work_items = tuple(
        WorkItem(
            id=item["id"],
            title=item["title"],
            description=item.get("description", ""),
            impact=int(item["impact"]),
            urgency=int(item["urgency"]),
            effort=int(item["effort"]),
            skills=tuple(item.get("skills", [])),
            dependencies=tuple(item.get("dependencies", [])),
            status=item.get("status", "todo"),
        )
        for item in data["work_items"]
    )
    return Project(
        name=data["name"],
        goal=data["goal"],
        timeline_weeks=int(data["timeline_weeks"]),
        team=team,
        work_items=work_items,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI-powered agentic workflow for project management")
    parser.add_argument("project_json", type=Path, help="Path to project definition JSON")
    parser.add_argument("--output", type=Path, help="Optional Markdown output path")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    project = load_project(args.project_json)
    plan = AgenticProjectManager().run(project)
    markdown = render_markdown(plan)

    if args.output:
        args.output.write_text(markdown, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(markdown)


if __name__ == "__main__":
    main()
