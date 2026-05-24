from __future__ import annotations

from .agents import IntakeAgent, PlanningAgent, PrioritizationAgent, ReporterAgent, ResourceAgent, RiskAgent
from .models import Project, ProjectPlan


class AgenticProjectManager:
    def __init__(self) -> None:
        self.intake_agent = IntakeAgent()
        self.prioritization_agent = PrioritizationAgent()
        self.planning_agent = PlanningAgent()
        self.resource_agent = ResourceAgent()
        self.risk_agent = RiskAgent()
        self.reporter_agent = ReporterAgent()

    def run(self, project: Project) -> ProjectPlan:
        project, intake_note = self.intake_agent.normalize(project)
        scored_items, priority_note = self.prioritization_agent.score(project)
        phases, planning_note = self.planning_agent.create_phases(scored_items)
        assignments, resource_note = self.resource_agent.assign(project, scored_items)
        risks, risk_note = self.risk_agent.analyze(project, scored_items)
        summary, reporter_note = self.reporter_agent.summarize(project, scored_items, risks)

        return ProjectPlan(
            project=project,
            scored_items=scored_items,
            phases=phases,
            assignments=assignments,
            risks=risks,
            executive_summary=summary,
            agent_notes={
                self.intake_agent.name: intake_note,
                self.prioritization_agent.name: priority_note,
                self.planning_agent.name: planning_note,
                self.resource_agent.name: resource_note,
                self.risk_agent.name: risk_note,
                self.reporter_agent.name: reporter_note,
            },
        )
