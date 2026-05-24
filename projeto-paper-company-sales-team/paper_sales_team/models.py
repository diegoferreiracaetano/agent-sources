from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


Segment = Literal["office", "printing", "packaging", "education", "retail"]
SustainabilityNeed = Literal["standard", "recycled", "certified"]
Urgency = Literal["low", "medium", "high"]
DealStage = Literal["new", "qualified", "proposal", "negotiation"]


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    use_case: Segment
    sustainability: SustainabilityNeed
    unit_price: float
    minimum_order_units: int
    margin: float


@dataclass(frozen=True)
class SalesOpportunity:
    company_name: str
    segment: Segment
    monthly_volume_units: int
    sustainability_need: SustainabilityNeed
    budget: float
    urgency: Urgency
    stage: DealStage = "new"
    notes: str = ""

    def validate(self) -> None:
        if not self.company_name.strip():
            raise ValueError("company_name is required")
        if self.monthly_volume_units < 1:
            raise ValueError("monthly_volume_units must be greater than zero")
        if self.budget <= 0:
            raise ValueError("budget must be greater than zero")


@dataclass(frozen=True)
class LeadScore:
    score: float
    tier: str
    rationale: str


@dataclass(frozen=True)
class ProductRecommendation:
    product: Product
    fit_score: float
    rationale: str


@dataclass(frozen=True)
class QuoteLine:
    product: Product
    quantity: int
    unit_price: float
    discount_rate: float

    @property
    def subtotal(self) -> float:
        return round(self.quantity * self.unit_price * (1 - self.discount_rate), 2)


@dataclass(frozen=True)
class Quote:
    lines: tuple[QuoteLine, ...]
    total: float
    within_budget: bool


@dataclass(frozen=True)
class Forecast:
    close_probability: float
    weighted_revenue: float
    rationale: str


@dataclass(frozen=True)
class SalesPlan:
    opportunity: SalesOpportunity
    lead_score: LeadScore
    recommendations: tuple[ProductRecommendation, ...]
    quote: Quote
    negotiation_strategy: tuple[str, ...]
    forecast: Forecast
    follow_up_steps: tuple[str, ...]
    executive_summary: str
    agent_notes: dict[str, str] = field(default_factory=dict)
