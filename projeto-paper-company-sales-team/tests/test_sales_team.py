import unittest

from paper_sales_team import PaperSalesTeam, SalesOpportunity


class PaperSalesTeamTest(unittest.TestCase):
    def test_generates_sales_plan(self) -> None:
        opportunity = SalesOpportunity(
            company_name="BrightPath Schools",
            segment="education",
            monthly_volume_units=900,
            sustainability_need="standard",
            budget=4200,
            urgency="high",
            stage="proposal",
        )

        plan = PaperSalesTeam().run(opportunity)

        self.assertGreater(plan.lead_score.score, 0)
        self.assertTrue(plan.recommendations)
        self.assertGreater(plan.quote.total, 0)
        self.assertTrue(plan.negotiation_strategy)
        self.assertGreater(plan.forecast.close_probability, 0)
        self.assertIn("SalesManagerAgent", plan.agent_notes)

    def test_rejects_invalid_opportunity(self) -> None:
        opportunity = SalesOpportunity(
            company_name="",
            segment="office",
            monthly_volume_units=0,
            sustainability_need="standard",
            budget=0,
            urgency="low",
        )

        with self.assertRaises(ValueError):
            PaperSalesTeam().run(opportunity)


if __name__ == "__main__":
    unittest.main()
