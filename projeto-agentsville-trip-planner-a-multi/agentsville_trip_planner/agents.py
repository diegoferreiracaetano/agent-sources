from __future__ import annotations

from .data import DESTINATIONS, STYLE_EXPERIENCES
from .models import BudgetBreakdown, DailyItinerary, Destination, TravelRequest


class DestinationAgent:
    name = "DestinationAgent"

    def choose(self, request: TravelRequest) -> tuple[Destination, float, str]:
        candidates = []
        trip_budget_per_day = request.budget / max(request.days * request.travelers, 1)

        for destination in DESTINATIONS:
            style_score = 35 if request.style in destination.styles else 10
            climate_score = 25 if request.climate in ("any", destination.climate) else 5
            budget_score = max(0, 25 - abs(destination.daily_cost - trip_budget_per_day) * 0.2)
            access_score = max(0, 15 - destination.travel_time_hours)
            score = style_score + climate_score + budget_score + access_score
            candidates.append((score, destination))

        score, destination = max(candidates, key=lambda item: item[0])
        note = (
            f"{destination.name} equilibra estilo {request.style}, clima {request.climate} "
            f"e custo diario estimado de {destination.daily_cost:.0f}."
        )
        return destination, round(score, 2), note


class BudgetAgent:
    name = "BudgetAgent"

    def estimate(self, request: TravelRequest, destination: Destination) -> tuple[BudgetBreakdown, str]:
        daily_total = destination.daily_cost * request.days * request.travelers
        lodging = daily_total * 0.38
        food = daily_total * 0.24
        local_transport = daily_total * 0.12
        activities = daily_total * 0.18
        buffer = min(request.budget * 0.12, max(request.budget - daily_total, 0))
        budget = BudgetBreakdown(
            lodging=round(lodging, 2),
            food=round(food, 2),
            local_transport=round(local_transport, 2),
            activities=round(activities, 2),
            buffer=round(buffer, 2),
        )
        note = f"Estimativa baseada em {request.days} dias para {request.travelers} viajante(s)."
        return budget, note


class LocalExpertAgent:
    name = "LocalExpertAgent"

    def recommend(self, request: TravelRequest, destination: Destination) -> tuple[tuple[str, ...], str]:
        style_experiences = STYLE_EXPERIENCES[request.style]
        destination_highlights = tuple(f"explorar {highlight}" for highlight in destination.highlights[:3])
        experiences = destination_highlights + style_experiences
        note = f"Recomendacoes combinam destaques de {destination.name} com perfil {request.style}."
        return experiences, note


class ItineraryAgent:
    name = "ItineraryAgent"

    def build(
        self,
        request: TravelRequest,
        destination: Destination,
        experiences: tuple[str, ...],
    ) -> tuple[tuple[DailyItinerary, ...], str]:
        days = []
        slots_by_pace = {
            "slow": ("chegada tranquila e reconhecimento", "experiencia principal", "jantar leve"),
            "balanced": ("bairro essencial", "experiencia principal", "programa local"),
            "packed": ("ponto classico cedo", "duas experiencias proximas", "noite em area animada"),
        }
        morning_default, afternoon_default, evening_default = slots_by_pace[request.pace]

        for index in range(request.days):
            first = experiences[index % len(experiences)]
            second = experiences[(index + 1) % len(experiences)]
            highlight = destination.highlights[index % len(destination.highlights)]
            days.append(
                DailyItinerary(
                    day=index + 1,
                    theme=f"{destination.name}: {highlight}",
                    morning=f"{morning_default}: {first}",
                    afternoon=f"{afternoon_default}: {second}",
                    evening=f"{evening_default} com foco em {request.style}",
                )
            )

        note = f"Roteiro criado em ritmo {request.pace}, evitando repeticao de experiencias."
        return tuple(days), note


class SafetyAgent:
    name = "SafetyAgent"

    def advise(self, request: TravelRequest, destination: Destination) -> tuple[tuple[str, ...], str]:
        notes = [
            "Reserve hospedagem em area bem conectada para reduzir deslocamentos longos.",
            "Mantenha copia digital de documentos e seguro viagem atualizado.",
            "Separe uma margem de emergencia fora do orcamento diario.",
        ]
        if destination.climate == "cold":
            notes.append("Inclua camadas termicas e planeje pausas por causa da altitude ou frio.")
        if destination.climate == "warm":
            notes.append("Priorize hidratacao, protetor solar e atividades externas fora do pico de calor.")
        if request.pace == "packed":
            notes.append("Confirme tempos de deslocamento antes de comprar ingressos com horario marcado.")
        return tuple(notes), "Notas de seguranca ajustadas ao clima e ao ritmo da viagem."
