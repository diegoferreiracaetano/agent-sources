from __future__ import annotations

from .models import Destination


DESTINATIONS: tuple[Destination, ...] = (
    Destination(
        name="Lisbon",
        country="Portugal",
        climate="mild",
        styles=("culture", "food", "family", "relax"),
        daily_cost=120,
        travel_time_hours=10,
        highlights=("Alfama", "Belem", "miradouros", "pastel de nata"),
    ),
    Destination(
        name="Buenos Aires",
        country="Argentina",
        climate="mild",
        styles=("culture", "food", "family"),
        daily_cost=85,
        travel_time_hours=3,
        highlights=("San Telmo", "Recoleta", "tango", "cafes historicos"),
    ),
    Destination(
        name="Cusco",
        country="Peru",
        climate="cold",
        styles=("adventure", "culture"),
        daily_cost=95,
        travel_time_hours=7,
        highlights=("Vale Sagrado", "Machu Picchu", "mercados andinos"),
    ),
    Destination(
        name="Florianopolis",
        country="Brazil",
        climate="warm",
        styles=("relax", "adventure", "family"),
        daily_cost=75,
        travel_time_hours=1.5,
        highlights=("Lagoa da Conceicao", "trilhas", "praias", "frutos do mar"),
    ),
    Destination(
        name="Mexico City",
        country="Mexico",
        climate="mild",
        styles=("culture", "food", "family"),
        daily_cost=100,
        travel_time_hours=9,
        highlights=("Roma Norte", "Coyoacan", "museus", "tacos"),
    ),
)


STYLE_EXPERIENCES: dict[str, tuple[str, ...]] = {
    "culture": (
        "visita guiada a um bairro historico",
        "museu principal com tempo livre para exploracao",
        "passeio arquitetonico pelo centro",
    ),
    "adventure": (
        "trilha ou atividade ao ar livre",
        "mirante panoramico no fim da tarde",
        "experiencia com guia local especializado",
    ),
    "relax": (
        "manha livre em area tranquila",
        "almoco longo em restaurante local",
        "fim de tarde em parque, praia ou jardim",
    ),
    "food": (
        "tour gastronomico com pratos tipicos",
        "mercado local com degustacoes",
        "jantar em restaurante recomendado por moradores",
    ),
    "family": (
        "atividade interativa para todas as idades",
        "parque ou atracao com boa infraestrutura",
        "roteiro com deslocamentos curtos",
    ),
}
