# Reflection

This agentic workflow is strongest as a reusable planning scaffold. The agent classes separate prompting, knowledge grounding, evaluation, routing, and planning responsibilities, which makes the system easier to extend for future InnovateNext product specs.

The main limitation is that the local fallback is deterministic and simpler than a real LLM-backed implementation. In production, the same class interfaces can use OpenAI calls through the configured API key, including `gpt-3.5-turbo` for chat completions and `text-embedding-3-large` for routing embeddings.

One specific improvement would be to add richer scoring to `EvaluationAgent`, such as per-criterion scores and revision histories, so TPMs can understand not only whether an artifact passed, but how close it was to meeting the expected standard.
