from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from workflow_agents.base_agents import KnowledgeAugmentedPromptAgent, RoutingAgent


env_path = Path(__file__).resolve().parents[1] / "tests" / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

openai_api_key = os.getenv("OPENAI_API_KEY")

texas_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona="Texas history expert",
    knowledge="Rome, Texas is a small community in the United States.",
)
europe_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona="European history expert",
    knowledge="Rome, Italy was the center of the Roman Empire.",
)
math_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona="Math expert",
    knowledge="To estimate effort, multiply days per story by number of stories.",
)

routing_agent = RoutingAgent(openai_api_key=openai_api_key)
routing_agent.agents = [
    {
        "name": "Texas Agent",
        "description": "Answers questions about Texas towns and Texas history",
        "func": lambda query: texas_agent.respond(query),
    },
    {
        "name": "Europe Agent",
        "description": "Answers questions about Rome Italy and European history",
        "func": lambda query: europe_agent.respond(query),
    },
    {
        "name": "Math Agent",
        "description": "Answers math, multiplication, estimation, story points, and effort questions",
        "func": lambda query: math_agent.respond(query),
    },
]

prompts = [
    "Tell me about the history of Rome, Texas",
    "Tell me about the history of Rome, Italy",
    "One story takes 2 days, and there are 20 stories",
]

print("RoutingAgent test")
for prompt in prompts:
    print("Prompt:", prompt)
    print("Response:", routing_agent.route(prompt))
print("PASS")
