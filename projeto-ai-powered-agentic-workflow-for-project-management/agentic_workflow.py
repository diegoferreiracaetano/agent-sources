from __future__ import annotations

import os
from pathlib import Path

from workflow_agents.base_agents import (
    ActionPlanningAgent,
    EvaluationAgent,
    KnowledgeAugmentedPromptAgent,
    RoutingAgent,
)


def load_env_file(path: Path) -> None:
    """Small .env loader so the project works without extra dependencies."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


PROJECT_ROOT = Path(__file__).resolve().parent
load_env_file(PROJECT_ROOT / "tests" / ".env")

# TODO 2: Load OpenAI API key from environment variables.
openai_api_key = os.getenv("OPENAI_API_KEY")

# TODO 3: Load the Email Router product specification.
product_spec = (PROJECT_ROOT / "Product-Spec-Email-Router.txt").read_text(encoding="utf-8")

workflow_prompt = (
    "Create a complete technical project management plan for the Email Router pilot. "
    "Generate user stories, product features, and detailed engineering tasks."
)

# TODO 4: Instantiate Action Planning Agent with provided planning knowledge.
knowledge_action_planning = (
    "A TPM planning workflow should first create user stories, then define product "
    "features, then create engineering tasks, and finally evaluate and assemble the output."
)
action_planning_agent = ActionPlanningAgent(
    openai_api_key=openai_api_key,
    knowledge=knowledge_action_planning,
)

# TODO 5 and TODO 6: Complete product manager knowledge with product_spec and instantiate.
persona_product_manager = "You are a Product Manager who writes clear agile user stories."
knowledge_product_manager = (
    "Create user stories only. Use this structure exactly: "
    "As a [type of user], I want [an action or feature] so that [benefit/value].\n\n"
    "Product specification:\n"
    + product_spec
)
product_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_product_manager,
    knowledge=knowledge_product_manager,
)

# TODO 7: Product Manager Evaluation Agent.
persona_product_manager_eval = "You are an evaluation agent that checks the answers of other worker agents"
evaluation_criteria_product_manager = (
    "The answer should be stories that follow the following structure: "
    "As a [type of user], I want [an action or feature] so that [benefit/value]."
)
product_manager_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_product_manager_eval,
    evaluation_criteria=evaluation_criteria_product_manager,
    agent_to_evaluate=product_manager_knowledge_agent,
    max_interactions=10,
)

# Program Manager knowledge agent and TODO 8 evaluator.
persona_program_manager = "You are a Program Manager who defines product features for engineering planning."
knowledge_program_manager = (
    "Create product features from a specification. Each feature must include "
    "Feature Name, Description, Key Functionality, and User Benefit.\n\n"
    "Product specification:\n"
    + product_spec
)
program_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_program_manager,
    knowledge=knowledge_program_manager,
)

persona_program_manager_eval = "You are an evaluation agent that checks Program Manager feature outputs"
evaluation_criteria_program_manager = (
    "The answer should be product features that follow the following structure: "
    "Feature Name: A clear, concise title that identifies the capability\n"
    "Description: A brief explanation of what the feature does and its purpose\n"
    "Key Functionality: The specific capabilities or actions the feature provides\n"
    "User Benefit: How this feature creates value for the user"
)
program_manager_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_program_manager_eval,
    evaluation_criteria=evaluation_criteria_program_manager,
    agent_to_evaluate=program_manager_knowledge_agent,
    max_interactions=10,
)

# Development Engineer knowledge agent and TODO 9 evaluator.
persona_dev_engineer = "You are a Development Engineer who converts product plans into implementation tasks."
knowledge_dev_engineer = (
    "Create engineering tasks from user stories and product features. Each task must "
    "include Task ID, Task Title, Related User Story, Description, Acceptance Criteria, "
    "Estimated Effort, and Dependencies.\n\n"
    "Product specification:\n"
    + product_spec
)
development_engineer_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_dev_engineer,
    knowledge=knowledge_dev_engineer,
)

persona_dev_engineer_eval = "You are an evaluation agent that checks Development Engineer task outputs"
evaluation_criteria_dev_engineer = (
    "The answer should be tasks following this exact structure: "
    "Task ID: A unique identifier  for tracking purposes\n"
    "Task Title: Brief description of the specific development work\n"
    "Related User Story: Reference to the parent user story\n"
    "Description: Detailed explanation of the technical work required\n"
    "Acceptance Criteria: Specific requirements that must be met for completion\n"
    "Estimated Effort: Time or complexity estimation\n"
    "Dependencies: Any tasks that must be completed first"
)
development_engineer_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_dev_engineer_eval,
    evaluation_criteria=evaluation_criteria_dev_engineer,
    agent_to_evaluate=development_engineer_knowledge_agent,
    max_interactions=10,
)


# TODO 11: Support functions for each routed team.
def product_manager_support_function(query: str) -> str:
    response = product_manager_knowledge_agent.respond(query)
    evaluation = product_manager_evaluation_agent.evaluate(response)
    return evaluation["final_response"]


def program_manager_support_function(query: str) -> str:
    response = program_manager_knowledge_agent.respond(query)
    evaluation = program_manager_evaluation_agent.evaluate(response)
    return evaluation["final_response"]


def development_engineer_support_function(query: str) -> str:
    response = development_engineer_knowledge_agent.respond(query)
    evaluation = development_engineer_evaluation_agent.evaluate(response)
    return evaluation["final_response"]


# TODO 10: Instantiate and configure Routing Agent.
routing_agent = RoutingAgent(openai_api_key=openai_api_key)
routing_agent.agents = [
    {
        "name": "Product Manager",
        "description": "Responsible for defining product personas and user stories only. Does not define features or engineering tasks.",
        "func": product_manager_support_function,
    },
    {
        "name": "Program Manager",
        "description": "Responsible for defining product features, descriptions, key functionality, and user benefits.",
        "func": program_manager_support_function,
    },
    {
        "name": "Development Engineer",
        "description": "Responsible for defining engineering tasks, task IDs, dependencies, acceptance criteria, and implementation work.",
        "func": development_engineer_support_function,
    },
]


def run_workflow(prompt: str = workflow_prompt) -> list[str]:
    """TODO 12: Run the full agentic workflow."""
    workflow_steps = action_planning_agent.extract_steps_from_prompt(prompt)
    completed_steps = []

    print("# AI-Powered Agentic Workflow for Project Management")
    print("\nPilot Product: Email Router")
    print("\n## Workflow Steps")

    for step in workflow_steps:
        print(f"\nProcessing step: {step}")
        result = routing_agent.route(step)
        completed_steps.append(result)
        print("Step Result:")
        print(result)

    print("\n## Final Output")
    for index, completed_step in enumerate(completed_steps, start=1):
        print(f"\n### Completed Step {index}")
        print(completed_step)

    return completed_steps


def main() -> None:
    run_workflow(workflow_prompt)


if __name__ == "__main__":
    main()
