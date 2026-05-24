from __future__ import annotations

from .models import TravelPlan


def money(value: float) -> str:
    return f"${value:,.2f}"


def render_markdown(plan: TravelPlan) -> str:
    destination = plan.destination
    budget = plan.budget
    lines = [
        f"# AgentsVille Trip Plan: {destination.name}, {destination.country}",
        "",
        f"**Pontuacao do destino:** {plan.score}/100",
        f"**Duracao:** {plan.request.days} dia(s)",
        f"**Perfil:** {plan.request.style} | clima {plan.request.climate} | ritmo {plan.request.pace}",
        "",
        "## Por que este destino",
        f"{destination.name} combina {', '.join(destination.styles)} com destaques como "
        f"{', '.join(destination.highlights)}.",
        "",
        "## Orcamento estimado",
        f"- Hospedagem: {money(budget.lodging)}",
        f"- Alimentacao: {money(budget.food)}",
        f"- Transporte local: {money(budget.local_transport)}",
        f"- Atividades: {money(budget.activities)}",
        f"- Reserva: {money(budget.buffer)}",
        f"- Total estimado: {money(budget.total)}",
        "",
        "## Experiencias recomendadas",
    ]

    lines.extend(f"- {experience}" for experience in plan.experiences)
    lines.extend(["", "## Roteiro diario"])

    for day in plan.itinerary:
        lines.extend(
            [
                f"### Dia {day.day}: {day.theme}",
                f"- Manha: {day.morning}",
                f"- Tarde: {day.afternoon}",
                f"- Noite: {day.evening}",
                "",
            ]
        )

    lines.append("## Seguranca e logistica")
    lines.extend(f"- {note}" for note in plan.safety_notes)
    lines.extend(["", "## Notas dos agentes"])
    lines.extend(f"- **{agent}:** {note}" for agent, note in plan.agent_notes.items())

    return "\n".join(lines)
