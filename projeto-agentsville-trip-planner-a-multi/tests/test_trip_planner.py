import unittest

from agentsville_trip_planner import TravelRequest, TripPlanner


class TripPlannerTest(unittest.TestCase):
    def test_builds_complete_plan(self) -> None:
        request = TravelRequest(
            origin="Sao Paulo",
            days=4,
            budget=1600,
            style="food",
            climate="mild",
            pace="balanced",
        )

        plan = TripPlanner().plan(request)

        self.assertEqual(len(plan.itinerary), 4)
        self.assertGreater(plan.score, 0)
        self.assertGreater(plan.budget.total, 0)
        self.assertTrue(plan.experiences)
        self.assertTrue(plan.safety_notes)
        self.assertIn("BudgetAgent", plan.agent_notes)

    def test_rejects_invalid_request(self) -> None:
        request = TravelRequest(origin="", days=0, budget=0)

        with self.assertRaises(ValueError):
            TripPlanner().plan(request)


if __name__ == "__main__":
    unittest.main()
