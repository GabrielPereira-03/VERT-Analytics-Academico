# VERT Analytics — versão acadêmica

Protótipo de gestão de SLA em Python e Streamlit. Dados integralmente fictícios e clientes anonimizados. Sem banco corporativo, autenticação corporativa ou API externa de IA.

## Executar

```bash
python -m pip install -r requirements.txt
python -m streamlit run demo_v3/app.py
```

Alternativa com Docker Desktop: `docker compose -f docker-compose.demo.yml up --build`. Acesse http://localhost:8502.

## Estrutura e funcionalidades

- `demo_v3/app.py`: dashboard, calculadora, assistente baseado em regras e relatórios.
- `demo_v3/data.py`: seis chamados sintéticos.
- `demo_v3/reports.py`: filtros, indicadores, PDF e Excel em memória.
- `sla_core/engine.py`: cálculo de horas úteis e corridas, pausas e projeção de vencimento.
- `tests/`: testes unitários.

## Testes

`python -m unittest discover -s tests -v`

## Experimente

Selecione novembro de 2026. Pergunte ao assistente: Quais chamados do CLIENTE-B estão em risco? / Gere relatório do CLIENTE-A em Excel.

## Limitações

Demonstração offline, sem monitoramento em tempo real. Metas e calendários ilustrativos, não regras contratuais homologadas. A taxa de cumprimento considera chamados fechados. Filtro por data de abertura. Conversas limitadas à sessão. Não utiliza IA generativa.
