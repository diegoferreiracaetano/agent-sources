from __future__ import annotations

from .models import ProjectPlan


def render_markdown(plan: ProjectPlan) -> str:
    assignments = {assignment.item_id: assignment for assignment in plan.assignments}
    lines = [
        f"# Project Plan: {plan.project.name}",
        "",
        f"**Goal:** {plan.project.goal}",
        f"**Timeline:** {plan.project.timeline_weeks} week(s)",
        "",
        "## Executive Summary",
        plan.executive_summary,
        "",
        "## Prioritized Work",
    ]

    for scored in plan.scored_items:
        assignment = assignments[scored.item.id]
        lines.append(
            f"- **{scored.item.id} - {scored.item.title}** "
            f"({scored.priority}, score {scored.score}) -> {assignment.assignee}"
        )

    lines.extend(["", "## Execution Phases"])
    for phase in plan.phases:
        lines.extend(
            [
                f"### {phase.name}",
                phase.objective,
                f"Items: {', '.join(phase.item_ids)}",
                "",
            ]
        )

    lines.append("## Assignments")
    for assignment in plan.assignments:
        lines.append(f"- **{assignment.item_id}:** {assignment.assignee}. {assignment.rationale}")

    lines.extend(["", "## Risks"])
    for risk in plan.risks:
        lines.append(f"- **{risk.level.upper()} - {risk.title}:** {risk.mitigation}")

    lines.extend(["", "## Agent Notes"])
    for agent, note in plan.agent_notes.items():
        lines.append(f"- **{agent}:** {note}")

    return "\n".join(lines)
