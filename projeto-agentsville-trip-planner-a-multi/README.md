# AgentsVille Trip Planner

Um assistente de viagens multiagente em Python. O projeto simula uma pequena "cidade" de agentes especializados que colaboram para transformar preferências do viajante em um plano de viagem estruturado.

## O que o sistema faz

- Inclui o notebook obrigatório da Udacity em `project_starter.ipynb`.
- Inclui a biblioteca de apoio do template em `project_lib.py`.
- Coleta preferências de viagem via CLI.
- Roteia a solicitação entre agentes especializados.
- Sugere destino, orçamento, atividades, roteiro diário e alertas.
- Consolida tudo em um plano final em Markdown.
- Inclui testes para o fluxo principal.

## Agentes

- `DestinationAgent`: escolhe o melhor destino com base em clima, orçamento, estilo e duração.
- `BudgetAgent`: estima custos de hospedagem, comida, transporte e atividades.
- `LocalExpertAgent`: recomenda experiências locais coerentes com o perfil do viajante.
- `ItineraryAgent`: monta o roteiro diário.
- `SafetyAgent`: adiciona dicas de segurança e logística.
- `CoordinatorAgent`: orquestra o fluxo e produz o plano final.

## Como rodar

Requer Python 3.10+.

Para a submissão da Udacity, abra e execute:

```bash
jupyter notebook project_starter.ipynb
```

Para testar a versão CLI local:

```bash
python3 -m agentsville_trip_planner.cli \
  --origin "Sao Paulo" \
  --days 5 \
  --budget 1800 \
  --style culture \
  --climate mild \
  --pace balanced
```

Também existe um exemplo pronto:

```bash
python3 examples/demo.py
```

## Testes

```bash
python3 -m unittest discover -s tests
```

## Estrutura

```text
agentsville_trip_planner/
  agents.py          # Agentes especializados
  cli.py             # Interface de linha de comando
  data.py            # Catálogo local de destinos e atividades
  models.py          # Modelos de domínio
  orchestrator.py    # Coordenação multiagente
  renderer.py        # Saída em Markdown
project_starter.ipynb # Notebook obrigatório da Udacity
project_lib.py        # Biblioteca do template da Udacity
examples/
  demo.py
tests/
  test_trip_planner.py
```

## Próximos passos sugeridos

- Integrar APIs reais de voos, hotéis e clima.
- Adicionar uma interface web.
- Persistir planos em JSON ou banco de dados.
- Trocar os agentes heurísticos por agentes LLM com ferramentas.
