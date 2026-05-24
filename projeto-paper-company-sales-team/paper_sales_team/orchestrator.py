from __future__ import annotations

from .agents import (
    FollowUpAgent,
    ForecastAgent,
    LeadQualificationAgent,
    NegotiationAgent,
    PricingAgent,
    ProductSpecialistAgent,
    SalesManagerAgent,
)
from .models import SalesOpportunity, SalesPlan


class PaperSalesTeam:
    def __init__(self) -> None:
        self.lead_agent = LeadQualificationAgent()
        self.product_agent = ProductSpecialistAgent()
        self.pricing_agent = PricingAgent()
        self.negotiation_agent = NegotiationAgent()
        self.forecast_agent = ForecastAgent()
        self.follow_up_agent = FollowUpAgent()
        self.manager_agent = SalesManagerAgent()

    def run(self, opportunity: SalesOpportunity) -> SalesPlan:
        lead_score, lead_note = self.lead_agent.qualify(opportunity)
        recommendations, product_note = self.product_agent.recommend(opportunity)
        quote, pricing_note = self.pricing_agent.quote(opportunity, recommendations)
        negotiation_strategy, negotiation_note = self.negotiation_agent.advise(opportunity, quote)
        forecast, forecast_note = self.forecast_agent.forecast(opportunity, lead_score, quote)
        follow_up_steps, follow_up_note = self.follow_up_agent.plan(opportunity, quote)
        summary, manager_note = self.manager_agent.summarize(opportunity, lead_score, forecast)

        return SalesPlan(
            opportunity=opportunity,
            lead_score=lead_score,
            recommendations=recommendations,
            quote=quote,
            negotiation_strategy=negotiation_strategy,
            forecast=forecast,
            follow_up_steps=follow_up_steps,
            executive_summary=summary,
            agent_notes={
                self.lead_agent.name: lead_note,
                self.product_agent.name: product_note,
                self.pricing_agent.name: pricing_note,
                self.negotiation_agent.name: negotiation_note,
                self.forecast_agent.name: forecast_note,
                self.follow_up_agent.name: follow_up_note,
                self.manager_agent.name: manager_note,
            },
        )
