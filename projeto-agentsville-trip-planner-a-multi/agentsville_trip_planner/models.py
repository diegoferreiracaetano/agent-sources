from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


TravelStyle = Literal["culture", "adventure", "relax", "food", "family"]
ClimatePreference = Literal["warm", "mild", "cold", "any"]
Pace = Literal["slow", "balanced", "packed"]


@dataclass(frozen=True)
class TravelRequest:
    origin: str
    days: int
    budget: float
    style: TravelStyle = "culture"
    climate: ClimatePreference = "any"
    pace: Pace = "balanced"
    travelers: int = 1

    def validate(self) -> None:
        if not self.origin.strip():
            raise ValueError("origin is required")
        if self.days < 1:
            raise ValueError("days must be at least 1")
        if self.budget <= 0:
            raise ValueError("budget must be greater than zero")
        if self.travelers < 1:
            raise ValueError("travelers must be at least 1")


@dataclass(frozen=True)
class Destination:
    name: str
    country: str
    climate: ClimatePreference
    styles: tuple[TravelStyle, ...]
    daily_cost: float
    travel_time_hours: float
    highlights: tuple[str, ...]


@dataclass(frozen=True)
class BudgetBreakdown:
    lodging: float
    food: float
    local_transport: float
    activities: float
    buffer: float

    @property
    def total(self) -> float:
        return self.lodging + self.food + self.local_transport + self.activities + self.buffer


@dataclass(frozen=True)
class DailyItinerary:
    day: int
    theme: str
    morning: str
    afternoon: str
    evening: str


@dataclass(frozen=True)
class TravelPlan:
    request: TravelRequest
    destination: Destination
    score: float
    budget: BudgetBreakdown
    experiences: tuple[str, ...]
    itinerary: tuple[DailyItinerary, ...]
    safety_notes: tuple[str, ...]
    agent_notes: dict[str, str] = field(default_factory=dict)
