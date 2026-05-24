from __future__ import annotations

from .catalog import CATALOG
from .models import (
    Forecast,
    LeadScore,
    Product,
    ProductRecommendation,
    Quote,
    QuoteLine,
    SalesOpportunity,
)


class LeadQualificationAgent:
    name = "LeadQualificationAgent"

    def qualify(self, opportunity: SalesOpportunity) -> tuple[LeadScore, str]:
        opportunity.validate()
        volume_score = min(40, opportunity.monthly_volume_units / 50)
        budget_score = min(25, opportunity.budget / 400)
        urgency_score = {"low": 5, "medium": 15, "high": 25}[opportunity.urgency]
        stage_score = {"new": 5, "qualified": 12, "proposal": 18, "negotiation": 22}[opportunity.stage]
        score = round(volume_score + budget_score + urgency_score + stage_score, 2)
        tier = "enterprise" if score >= 75 else "growth" if score >= 50 else "standard"
        rationale = f"{tier.title()} tier based on volume, budget, urgency and stage."
        return LeadScore(score=score, tier=tier, rationale=rationale), "Lead qualified with commercial fit scoring."


class ProductSpecialistAgent:
    name = "ProductSpecialistAgent"

    def recommend(self, opportunity: SalesOpportunity) -> tuple[tuple[ProductRecommendation, ...], str]:
        recommendations = []
        for product in CATALOG:
            segment_score = 45 if product.use_case == opportunity.segment else 10
            sustainability_score = 30 if product.sustainability == opportunity.sustainability_need else 12
            volume_score = 15 if opportunity.monthly_volume_units >= product.minimum_order_units else 5
            affordability_score = 10 if product.unit_price * product.minimum_order_units <= opportunity.budget else 2
            fit_score = segment_score + sustainability_score + volume_score + affordability_score
            rationale = (
                f"Matches {product.use_case} use case and {product.sustainability} sustainability profile."
            )
            recommendations.append(ProductRecommendation(product=product, fit_score=fit_score, rationale=rationale))

        recommendations.sort(key=lambda recommendation: recommendation.fit_score, reverse=True)
        return tuple(recommendations[:3]), "Top products ranked by segment, sustainability, volume and budget fit."


class PricingAgent:
    name = "PricingAgent"

    def quote(self, opportunity: SalesOpportunity, recommendations: tuple[ProductRecommendation, ...]) -> tuple[Quote, str]:
        if not recommendations:
            raise ValueError("at least one product recommendation is required")

        primary = recommendations[0].product
        quantity = max(opportunity.monthly_volume_units, primary.minimum_order_units)
        discount_rate = self._discount_for(quantity, primary)
        line = QuoteLine(
            product=primary,
            quantity=quantity,
            unit_price=primary.unit_price,
            discount_rate=discount_rate,
        )
        total = line.subtotal
        quote = Quote(lines=(line,), total=total, within_budget=total <= opportunity.budget)
        return quote, f"Quoted primary SKU {primary.sku} with {discount_rate:.0%} volume discount."

    def _discount_for(self, quantity: int, product: Product) -> float:
        if quantity >= product.minimum_order_units * 8:
            return min(0.16, product.margin * 0.5)
        if quantity >= product.minimum_order_units * 4:
            return min(0.10, product.margin * 0.35)
        if quantity >= product.minimum_order_units * 2:
            return min(0.06, product.margin * 0.25)
        return 0.0


class NegotiationAgent:
    name = "NegotiationAgent"

    def advise(self, opportunity: SalesOpportunity, quote: Quote) -> tuple[tuple[str, ...], str]:
        steps = []
        if quote.within_budget:
            steps.append("Anchor on reliability, delivery consistency and product fit instead of deeper discounting.")
        else:
            steps.append("Offer a phased first order or alternate SKU to get closer to budget.")
        if opportunity.sustainability_need != "standard":
            steps.append("Emphasize sustainability documentation and procurement compliance.")
        if opportunity.urgency == "high":
            steps.append("Create a fast-close option with limited-time delivery slot confirmation.")
        steps.append("Ask for monthly reorder cadence and decision criteria before sending final proposal.")
        return tuple(steps), "Negotiation strategy aligned to budget, urgency and sustainability need."


class ForecastAgent:
    name = "ForecastAgent"

    def forecast(self, opportunity: SalesOpportunity, lead_score: LeadScore, quote: Quote) -> tuple[Forecast, str]:
        stage_factor = {"new": 0.18, "qualified": 0.35, "proposal": 0.52, "negotiation": 0.68}[opportunity.stage]
        score_factor = min(0.22, lead_score.score / 400)
        budget_factor = 0.08 if quote.within_budget else -0.08
        urgency_factor = {"low": -0.03, "medium": 0.02, "high": 0.07}[opportunity.urgency]
        probability = min(0.9, max(0.05, stage_factor + score_factor + budget_factor + urgency_factor))
        weighted_revenue = round(quote.total * probability, 2)
        rationale = "Probability combines pipeline stage, fit score, budget fit and urgency."
        return Forecast(round(probability, 2), weighted_revenue, rationale), "Forecast generated from lead and quote signals."


class FollowUpAgent:
    name = "FollowUpAgent"

    def plan(self, opportunity: SalesOpportunity, quote: Quote) -> tuple[tuple[str, ...], str]:
        steps = [
            "Day 0: send quote with recommended SKU, quantity, discount and delivery assumptions.",
            "Day 2: confirm product specs, purchasing process and expected monthly reorder cadence.",
        ]
        if quote.within_budget:
            steps.append("Day 5: ask for purchase order or procurement onboarding next step.")
        else:
            steps.append("Day 5: propose revised quantity or alternate SKU to close the budget gap.")
        steps.append("Day 10: share reorder program and volume discount schedule.")
        return tuple(steps), "Follow-up cadence built for a B2B paper sales cycle."


class SalesManagerAgent:
    name = "SalesManagerAgent"

    def summarize(self, opportunity: SalesOpportunity, lead_score: LeadScore, forecast: Forecast) -> tuple[str, str]:
        summary = (
            f"{opportunity.company_name} is a {lead_score.tier} opportunity with score {lead_score.score}. "
            f"Expected close probability is {forecast.close_probability:.0%}, "
            f"with weighted revenue of ${forecast.weighted_revenue:,.2f}."
        )
        return summary, "Sales summary consolidated for manager review."
