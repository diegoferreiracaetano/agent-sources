# Paper Company Sales Team

Um sistema agentic em Python que simula uma equipe de vendas para uma empresa de papel. O fluxo recebe leads, recomenda produtos do catálogo, calcula cotações, estima probabilidade de fechamento e gera follow-ups comerciais.

## O que o projeto faz

- Lê uma oportunidade de venda em JSON.
- Qualifica o lead por volume, segmento e urgência.
- Recomenda produtos de papel a partir de uso, sustentabilidade e orçamento.
- Calcula cotação com descontos por volume.
- Sugere estratégia de negociação e próximos passos.
- Produz um relatório comercial em Markdown.
- Inclui CLI, exemplo e testes.

## Agentes

- `LeadQualificationAgent`: pontua o lead e identifica potencial.
- `ProductSpecialistAgent`: recomenda SKUs do catálogo.
- `PricingAgent`: monta cotação com desconto por volume.
- `NegotiationAgent`: sugere abordagem comercial.
- `ForecastAgent`: estima probabilidade de fechamento e receita ponderada.
- `FollowUpAgent`: cria plano de follow-up.
- `SalesManagerAgent`: consolida o resumo executivo.

## Como rodar

Requer Python 3.10+.

```bash
python3 -m paper_sales_team.cli examples/sample_opportunity.json
```

Com saída em arquivo:

```bash
python3 -m paper_sales_team.cli examples/sample_opportunity.json --output sales-brief.md
```

## Testes

```bash
python3 -m unittest discover -s tests
```

## Estrutura

```text
paper_sales_team/
  agents.py          # Agentes de vendas
  catalog.py         # Catálogo de produtos
  cli.py             # Interface de linha de comando
  models.py          # Modelos de domínio
  orchestrator.py    # Coordenação do time agentic
  renderer.py        # Relatório Markdown
examples/
  sample_opportunity.json
tests/
  test_sales_team.py
```

## Próximos passos

- Integrar CRM como HubSpot, Salesforce ou Pipedrive.
- Conectar ERP/estoque para disponibilidade real.
- Gerar propostas em PDF.
- Adicionar envio automático de e-mail de follow-up.
