import unittest

from agentic_pm import AgenticProjectManager, Project, TeamMember, WorkItem


class AgenticProjectManagerTest(unittest.TestCase):
    def test_generates_project_plan(self) -> None:
        project = Project(
            name="Launch",
            goal="Ship a small product launch",
            timeline_weeks=2,
            team=(
                TeamMember(name="Ana", skills=("frontend", "testing"), capacity=5),
                TeamMember(name="Bruno", skills=("backend",), capacity=5),
            ),
            work_items=(
                WorkItem("A", "API", "Build API", impact=5, urgency=5, effort=3, skills=("backend",)),
                WorkItem("B", "UI", "Build UI", impact=4, urgency=4, effort=3, skills=("frontend",), dependencies=("A",)),
            ),
        )

        plan = AgenticProjectManager().run(project)

        self.assertEqual(len(plan.scored_items), 2)
        self.assertTrue(plan.phases)
        self.assertEqual(len(plan.assignments), 2)
        self.assertTrue(plan.risks)
        self.assertIn("PrioritizationAgent", plan.agent_notes)

    def test_rejects_duplicate_work_item_ids(self) -> None:
        project = Project(
            name="Bad Project",
            goal="Catch duplicate IDs",
            timeline_weeks=1,
            team=(TeamMember(name="Ana", skills=("ops",), capacity=2),),
            work_items=(
                WorkItem("A", "One", "", impact=3, urgency=3, effort=1),
                WorkItem("A", "Two", "", impact=3, urgency=3, effort=1),
            ),
        )

        with self.assertRaises(ValueError):
            AgenticProjectManager().run(project)


if __name__ == "__main__":
    unittest.main()
