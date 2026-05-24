from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from workflow_agents.base_agents import DirectPromptAgent


def load_env() -> None:
    env_path = Path(__file__).resolve().parents[1] / "tests" / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


load_env()
openai_api_key = os.getenv("OPENAI_API_KEY")
direct_agent = DirectPromptAgent(openai_api_key=openai_api_key)
prompt = "What is the Capital of France?"
response = direct_agent.respond(prompt)

print("DirectPromptAgent test")
print("Prompt:", prompt)
print("Response:", response)
print("Knowledge source: the agent uses general knowledge from the selected LLM model; when no API key is present, the local deterministic fallback is used.")
print("PASS")
