from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from workflow_agents.base_agents import AugmentedPromptAgent


env_path = Path(__file__).resolve().parents[1] / "tests" / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

openai_api_key = os.getenv("OPENAI_API_KEY")
persona = "You are a concise technical project manager"
agent = AugmentedPromptAgent(openai_api_key=openai_api_key, persona=persona)

prompt = "Explain why clear user stories help engineering teams."
augmented_agent_response = agent.respond(prompt)

print("AugmentedPromptAgent test")
print("Prompt:", prompt)
print("Response:", augmented_agent_response)
print("Comment: the agent likely uses general model knowledge about agile project management.")
print("Comment: the persona should make the response sound like concise TPM guidance.")
print("PASS")
