from __future__ import annotations

from .agents import (
    BudgetAgent,
    DestinationAgent,
    ItineraryAgent,
    LocalExpertAgent,
    SafetyAgent,
)
from .models import TravelPlan, TravelRequest


class TripPlanner:
    def __init__(self) -> None:
        self.destination_agent = DestinationAgent()
        self.budget_agent = BudgetAgent()
        self.local_expert_agent = LocalExpertAgent()
        self.itinerary_agent = ItineraryAgent()
        self.safety_agent = SafetyAgent()

    def plan(self, request: TravelRequest) -> TravelPlan:
        request.validate()

        destination, score, destination_note = self.destination_agent.choose(request)
        budget, budget_note = self.budget_agent.estimate(request, destination)
        experiences, local_note = self.local_expert_agent.recommend(request, destination)
        itinerary, itinerary_note = self.itinerary_agent.build(request, destination, experiences)
        safety_notes, safety_note = self.safety_agent.advise(request, destination)

        return TravelPlan(
            request=request,
            destination=destination,
            score=score,
            budget=budget,
            experiences=experiences,
            itinerary=itinerary,
            safety_notes=safety_notes,
            agent_notes={
                self.destination_agent.name: destination_note,
                self.budget_agent.name: budget_note,
                self.local_expert_agent.name: local_note,
                self.itinerary_agent.name: itinerary_note,
                self.safety_agent.name: safety_note,
            },
        )
