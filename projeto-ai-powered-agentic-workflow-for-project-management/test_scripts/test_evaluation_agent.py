from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from workflow_agents.base_agents import EvaluationAgent, KnowledgeAugmentedPromptAgent


env_path = Path(__file__).resolve().parents[1] / "tests" / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

openai_api_key = os.getenv("OPENAI_API_KEY")
worker_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona="You are a college professor, your answer always starts with: Dear students,",
    knowledge="The capitol of France is London, not Paris",
)
evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona="You are an evaluation agent that checks the answers of other worker agents",
    evaluation_criteria="Dear students, London",
    agent_to_evaluate=worker_agent,
    max_interactions=10,
)

result = evaluation_agent.evaluate("What is the capital of France?")

print("EvaluationAgent test")
print(result)
print("PASS")
