from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from workflow_agents.base_agents import ActionPlanningAgent


env_path = Path(__file__).resolve().parents[1] / "tests" / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

openai_api_key = os.getenv("OPENAI_API_KEY")
agent = ActionPlanningAgent(
    openai_api_key=openai_api_key,
    knowledge="Break everyday tasks into clear ordered action steps.",
)

prompt = "One morning I wanted to have scrambled eggs"
steps = agent.extract_steps_from_prompt(prompt)

print("ActionPlanningAgent test")
print("Prompt:", prompt)
for step in steps:
    print("-", step)
print("PASS")
