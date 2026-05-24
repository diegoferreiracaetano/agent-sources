# AI-Powered Agentic Workflow for Project Management

Submissão para o projeto **AI-Powered Agentic Workflow for Project Management**. O piloto usa a especificação `Product-Spec-Email-Router.txt` para demonstrar um workflow agentic que transforma uma ideia de produto em user stories, features e engineering tasks.

## Environment

Para usar chamadas reais da OpenAI, crie `tests/.env` com:

```text
OPENAI_API_KEY=your_openai_api_key
```

Sem API key, os agentes usam fallback determinístico local para permitir execução e revisão offline.

## Phase 1: Agentic Toolkit

O pacote `workflow_agents` contém sete agentes reutilizáveis em `workflow_agents/base_agents.py`:

- `DirectPromptAgent`
- `AugmentedPromptAgent`
- `KnowledgeAugmentedPromptAgent`
- `RAGKnowledgePromptAgent`
- `EvaluationAgent`
- `RoutingAgent`
- `ActionPlanningAgent`

Scripts de teste independentes:

```bash
python3 direct_prompt_agent.py
python3 augmented_prompt_agent.py
python3 knowledge_augmented_prompt_agent.py
python3 rag_knowledge_prompt_agent.py
python3 evaluation_agent.py
python3 routing_agent.py
python3 action_planning_agent.py
```

Evidência de execução:

- `test_outputs/agent_tests_output.txt`

## Phase 2: Project Management Workflow

O script principal é:

```bash
python3 agentic_workflow.py
```

Ele orquestra:

- `ActionPlanningAgent` para decompor a solicitação de TPM.
- `RoutingAgent` para rotear subtarefas para Product Manager, Program Manager e Development Engineer.
- `KnowledgeAugmentedPromptAgent` para gerar user stories, features e engineering tasks com base no spec.
- `EvaluationAgent` para validar cada artefato.

Evidência de execução:

- `test_outputs/agentic_workflow_output.txt`

## Arquivos Principais Para Submissão

```text
workflow_agents/base_agents.py
requirements.txt
direct_prompt_agent.py
augmented_prompt_agent.py
knowledge_augmented_prompt_agent.py
rag_knowledge_prompt_agent.py
evaluation_agent.py
routing_agent.py
action_planning_agent.py
test_scripts/
test_outputs/agent_tests_output.txt
Product-Spec-Email-Router.txt
agentic_workflow.py
test_outputs/agentic_workflow_output.txt
reflection.md
```

## Verificação Extra

O projeto também preserva o pacote inicial `agentic_pm` com testes `unittest`:

```bash
python3 -m unittest discover -s tests
```
