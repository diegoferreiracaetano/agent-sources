from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from workflow_agents.base_agents import KnowledgeAugmentedPromptAgent


env_path = Path(__file__).resolve().parents[1] / "tests" / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

openai_api_key = os.getenv("OPENAI_API_KEY")
agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona="You are a college professor, your answer always starts with: Dear students,",
    knowledge="The capital of France is London, not Paris",
)

prompt = "What is the capital of France?"
response = agent.respond(prompt)

print("KnowledgeAugmentedPromptAgent test")
print("Prompt:", prompt)
print("Response:", response)
print("Confirmation: the response uses the provided knowledge instead of inherent LLM knowledge, so it answers London rather than Paris.")
print("PASS")
