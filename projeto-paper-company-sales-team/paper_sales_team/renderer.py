from __future__ import annotations

from .models import SalesPlan


def money(value: float) -> str:
    return f"${value:,.2f}"


def render_markdown(plan: SalesPlan) -> str:
    opportunity = plan.opportunity
    lines = [
        f"# Paper Sales Brief: {opportunity.company_name}",
        "",
        f"**Segment:** {opportunity.segment}",
        f"**Monthly volume:** {opportunity.monthly_volume_units} units",
        f"**Sustainability need:** {opportunity.sustainability_need}",
        f"**Budget:** {money(opportunity.budget)}",
        f"**Stage:** {opportunity.stage}",
        "",
        "## Executive Summary",
        plan.executive_summary,
        "",
        "## Lead Qualification",
        f"- Score: {plan.lead_score.score}",
        f"- Tier: {plan.lead_score.tier}",
        f"- Rationale: {plan.lead_score.rationale}",
        "",
        "## Product Recommendations",
    ]

    for recommendation in plan.recommendations:
        product = recommendation.product
        lines.append(
            f"- **{product.sku} - {product.name}:** fit {recommendation.fit_score}; "
            f"{money(product.unit_price)} per unit. {recommendation.rationale}"
        )

    lines.extend(["", "## Quote"])
    for line in plan.quote.lines:
        lines.append(
            f"- **{line.product.sku}:** {line.quantity} units x {money(line.unit_price)} "
            f"with {line.discount_rate:.0%} discount = {money(line.subtotal)}"
        )
    lines.append(f"- **Total:** {money(plan.quote.total)}")
    lines.append(f"- **Within budget:** {'yes' if plan.quote.within_budget else 'no'}")

    lines.extend(["", "## Negotiation Strategy"])
    lines.extend(f"- {step}" for step in plan.negotiation_strategy)

    lines.extend(
        [
            "",
            "## Forecast",
            f"- Close probability: {plan.forecast.close_probability:.0%}",
            f"- Weighted revenue: {money(plan.forecast.weighted_revenue)}",
            f"- Rationale: {plan.forecast.rationale}",
            "",
            "## Follow-Up Plan",
        ]
    )
    lines.extend(f"- {step}" for step in plan.follow_up_steps)

    lines.extend(["", "## Agent Notes"])
    lines.extend(f"- **{agent}:** {note}" for agent, note in plan.agent_notes.items())

    return "\n".join(lines)
