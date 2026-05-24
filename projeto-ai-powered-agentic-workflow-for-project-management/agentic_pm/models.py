from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


Priority = Literal["low", "medium", "high", "critical"]
Status = Literal["todo", "in_progress", "blocked", "done"]


@dataclass(frozen=True)
class WorkItem:
    id: str
    title: str
    description: str
    impact: int
    urgency: int
    effort: int
    skills: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    status: Status = "todo"

    def validate(self) -> None:
        if not self.id.strip():
            raise ValueError("work item id is required")
        if not self.title.strip():
            raise ValueError(f"work item {self.id} requires a title")
        for field_name, value in (("impact", self.impact), ("urgency", self.urgency), ("effort", self.effort)):
            if value < 1 or value > 5:
                raise ValueError(f"{field_name} for {self.id} must be between 1 and 5")


@dataclass(frozen=True)
class TeamMember:
    name: str
    skills: tuple[str, ...]
    capacity: int

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("team member name is required")
        if self.capacity < 1:
            raise ValueError(f"capacity for {self.name} must be at least 1")


@dataclass(frozen=True)
class Project:
    name: str
    goal: str
    timeline_weeks: int
    team: tuple[TeamMember, ...]
    work_items: tuple[WorkItem, ...]

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("project name is required")
        if self.timeline_weeks < 1:
            raise ValueError("timeline_weeks must be at least 1")
        if not self.team:
            raise ValueError("project requires at least one team member")
        if not self.work_items:
            raise ValueError("project requires at least one work item")
        for member in self.team:
            member.validate()
        for item in self.work_items:
            item.validate()


@dataclass(frozen=True)
class ScoredItem:
    item: WorkItem
    score: float
    priority: Priority


@dataclass(frozen=True)
class Assignment:
    item_id: str
    assignee: str
    rationale: str


@dataclass(frozen=True)
class Phase:
    name: str
    item_ids: tuple[str, ...]
    objective: str


@dataclass(frozen=True)
class Risk:
    level: Priority
    title: str
    mitigation: str


@dataclass(frozen=True)
class ProjectPlan:
    project: Project
    scored_items: tuple[ScoredItem, ...]
    phases: tuple[Phase, ...]
    assignments: tuple[Assignment, ...]
    risks: tuple[Risk, ...]
    executive_summary: str
    agent_notes: dict[str, str] = field(default_factory=dict)
