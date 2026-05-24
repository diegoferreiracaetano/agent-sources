from __future__ import annotations

from collections import defaultdict

from .models import Assignment, Phase, Priority, Project, Risk, ScoredItem, WorkItem


class IntakeAgent:
    name = "IntakeAgent"

    def normalize(self, project: Project) -> tuple[Project, str]:
        project.validate()
        seen = set()
        for item in project.work_items:
            if item.id in seen:
                raise ValueError(f"duplicate work item id: {item.id}")
            seen.add(item.id)
        return project, f"Validated {len(project.work_items)} work items and {len(project.team)} team members."


class PrioritizationAgent:
    name = "PrioritizationAgent"

    def score(self, project: Project) -> tuple[tuple[ScoredItem, ...], str]:
        scored = []
        dependency_counts = defaultdict(int)
        for item in project.work_items:
            for dependency in item.dependencies:
                dependency_counts[dependency] += 1

        for item in project.work_items:
            dependency_bonus = dependency_counts[item.id] * 0.6
            blocker_penalty = len(item.dependencies) * 0.35
            score = (item.impact * 2.0) + (item.urgency * 1.7) - (item.effort * 0.8)
            score += dependency_bonus - blocker_penalty
            scored.append(ScoredItem(item=item, score=round(score, 2), priority=self._priority(score)))

        scored.sort(key=lambda entry: entry.score, reverse=True)
        return tuple(scored), "Priorities combine impact, urgency, effort and dependency leverage."

    def _priority(self, score: float) -> Priority:
        if score >= 13:
            return "critical"
        if score >= 10:
            return "high"
        if score >= 7:
            return "medium"
        return "low"


class PlanningAgent:
    name = "PlanningAgent"

    def create_phases(self, scored_items: tuple[ScoredItem, ...]) -> tuple[tuple[Phase, ...], str]:
        critical = tuple(entry.item.id for entry in scored_items if entry.priority in ("critical", "high"))
        medium = tuple(entry.item.id for entry in scored_items if entry.priority == "medium")
        low = tuple(entry.item.id for entry in scored_items if entry.priority == "low")

        phases = [
            Phase("Phase 1 - Foundation", critical, "Unlock the most valuable and blocking work first."),
            Phase("Phase 2 - Delivery", medium, "Build the main project outcomes after core risks are reduced."),
            Phase("Phase 3 - Polish", low, "Handle lower priority enhancements and finishing touches."),
        ]
        phases = [phase for phase in phases if phase.item_ids]
        return tuple(phases), f"Created {len(phases)} execution phases from prioritized work."


class ResourceAgent:
    name = "ResourceAgent"

    def assign(self, project: Project, scored_items: tuple[ScoredItem, ...]) -> tuple[tuple[Assignment, ...], str]:
        remaining_capacity = {member.name: member.capacity for member in project.team}
        assignments = []

        for scored in scored_items:
            item = scored.item
            candidates = sorted(
                project.team,
                key=lambda member: (
                    self._skill_overlap(item, member.skills),
                    remaining_capacity[member.name],
                ),
                reverse=True,
            )
            assignee = candidates[0]
            remaining_capacity[assignee.name] = max(0, remaining_capacity[assignee.name] - item.effort)
            overlap = self._skill_overlap(item, assignee.skills)
            rationale = f"Skill match {overlap}/{max(len(item.skills), 1)} with remaining capacity considered."
            assignments.append(Assignment(item_id=item.id, assignee=assignee.name, rationale=rationale))

        return tuple(assignments), "Assigned work by skill match and available capacity."

    def _skill_overlap(self, item: WorkItem, member_skills: tuple[str, ...]) -> int:
        return len(set(item.skills).intersection(member_skills))


class RiskAgent:
    name = "RiskAgent"

    def analyze(self, project: Project, scored_items: tuple[ScoredItem, ...]) -> tuple[tuple[Risk, ...], str]:
        total_effort = sum(item.effort for item in project.work_items)
        total_capacity = sum(member.capacity for member in project.team) * project.timeline_weeks
        blocked_items = [item for item in project.work_items if item.dependencies]
        critical_items = [entry for entry in scored_items if entry.priority == "critical"]
        risks = []

        if total_effort > total_capacity:
            risks.append(
                Risk(
                    level="critical",
                    title="Capacity is below estimated effort",
                    mitigation="Reduce scope, extend timeline, or add team capacity before execution starts.",
                )
            )
        if len(blocked_items) >= max(2, len(project.work_items) // 3):
            risks.append(
                Risk(
                    level="high",
                    title="Dependency chain may delay delivery",
                    mitigation="Review dependencies in planning and start unblockers in the first phase.",
                )
            )
        if len(critical_items) > 3:
            risks.append(
                Risk(
                    level="medium",
                    title="Too many critical items compete for attention",
                    mitigation="Confirm the top three outcomes with stakeholders and sequence the rest.",
                )
            )
        if not risks:
            risks.append(
                Risk(
                    level="low",
                    title="No major structural risk detected",
                    mitigation="Keep weekly reviews to catch scope drift early.",
                )
            )

        return tuple(risks), f"Analyzed effort {total_effort} against capacity {total_capacity}."


class ReporterAgent:
    name = "ReporterAgent"

    def summarize(self, project: Project, scored_items: tuple[ScoredItem, ...], risks: tuple[Risk, ...]) -> tuple[str, str]:
        top_items = ", ".join(entry.item.title for entry in scored_items[:3])
        highest_risk = max(risks, key=lambda risk: ["low", "medium", "high", "critical"].index(risk.level))
        summary = (
            f"{project.name} is planned over {project.timeline_weeks} week(s). "
            f"The highest value work is: {top_items}. "
            f"Primary risk: {highest_risk.title}."
        )
        return summary, "Generated concise executive summary from priorities and risks."
