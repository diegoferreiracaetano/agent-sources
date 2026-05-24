from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from workflow_agents import RAGKnowledgePromptAgent


def fake_llm(prompt: str) -> str:
    return prompt


documents = {
    "routing": "Routing assigns emails to queues based on intent and urgency.",
    "audit": "Audit logs store routing decisions, confidence, and model version.",
    "billing": "Billing inquiries should route to the Billing queue.",
}
agent = RAGKnowledgePromptAgent(
    role="Retrieval Agent",
    documents=documents,
    instructions="Use retrieved context to answer.",
    llm=fake_llm,
)
retrieved = agent.retrieve("How should routing decisions be audited?", top_k=2)
result = agent.run("How should routing decisions be audited?")

print("RAGKnowledgePromptAgent test")
print("Retrieved:", retrieved)
print(result)
assert retrieved
assert "Audit logs" in result or "Routing assigns" in result
print("PASS")
