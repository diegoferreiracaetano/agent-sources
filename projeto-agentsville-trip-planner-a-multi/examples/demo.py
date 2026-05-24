from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agentsville_trip_planner import TravelRequest, TripPlanner
from agentsville_trip_planner.renderer import render_markdown


request = TravelRequest(
    origin="Sao Paulo",
    days=5,
    budget=1800,
    style="culture",
    climate="mild",
    pace="balanced",
    travelers=1,
)

plan = TripPlanner().plan(request)
print(render_markdown(plan))
