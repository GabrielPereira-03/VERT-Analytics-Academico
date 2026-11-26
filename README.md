# VERT Analytics | Gestão de SLA e assistente operacional

**[Conheça o projeto e experimente o VERT AI no navegador](https://gabrielpereira-03.github.io/VERT-Analytics-Site/)**

## Sobre o projeto

Desenvolvi o VERT Analytics pensando em uma necessidade do ambiente de trabalho da VERT: facilitar o acompanhamento dos chamados de suporte e tornar as informações sobre prazos de atendimento mais acessíveis para quem precisa tomar decisões no dia a dia.

A ideia foi reunir em uma única plataforma o cálculo de SLA, os indicadores de atendimento, a consulta de chamados e a geração de relatórios. Em vez de depender apenas de consultas manuais e cálculos separados, a proposta é permitir que o usuário encontre as informações de que precisa de forma mais prática.

O projeto começou com o foco no cálculo de SLA e evoluiu para uma ferramenta de análise, tendo como principal destaque o VERT AI, um assistente operacional que permite interagir com os dados por meio de perguntas em linguagem natural.

## Para quem desenvolvi o sistema?

O sistema foi pensado para o contexto operacional da VERT, especialmente para profissionais de suporte técnico, analistas de atendimento, equipes responsáveis pelo acompanhamento de contratos e gestores que precisam acompanhar indicadores e prazos.

Cada um desses profissionais tem necessidades diferentes. Um analista pode querer entender quanto tempo de SLA um chamado já consumiu, enquanto um gestor pode precisar de uma visão consolidada dos atendimentos ou de um relatório por contrato. A proposta do VERT Analytics é atender a essas necessidades dentro de uma mesma ferramenta.

Este repositório é uma versão acadêmica separada do ambiente corporativo, preparada para apresentar o desenvolvimento e os conceitos do sistema sem expor informações internas.

## O que é SLA?

SLA (Service Level Agreement), ou acordo de nível de serviço, estabelece compromissos de atendimento, incluindo os prazos que devem ser respeitados. O cálculo desses prazos pode envolver horários de expediente, finais de semana, feriados e períodos em que a contagem deve ser interrompida.

O motor de cálculo do projeto foi desenvolvido para trabalhar com essas condições de forma parametrizável. Na demonstração, as metas e os calendários são ilustrativos e não representam obrigações contratuais reais.

## VERT AI — o principal destaque do projeto

Uma das minhas prioridades foi tornar a consulta de informações mais natural. Por isso, desenvolvi um assistente que permite ao usuário fazer perguntas sem precisar conhecer a estrutura dos dados ou escrever comandos de programação.

Na versão Streamlit acadêmica, o assistente interpreta termos da pergunta, identifica o contrato, o período e o formato de relatório solicitado. Em seguida, consulta os registros fictícios e apresenta os resultados encontrados.

Alguns exemplos de perguntas:

- Quais chamados do CLIENTE-B estão em risco?
- Quais chamados violaram o SLA?
- Mostre um resumo do CLIENTE-A.
- Gere um relatório do CLIENTE-B em Excel.
- Relatório do CLIENTE-A de 01/11/2026 a 19/11/2026 em PDF.

O funcionamento é baseado em regras programadas em Python, tratamento de texto e expressões regulares. Não utilizei uma API externa de inteligência artificial generativa para produzir as respostas do assistente. As respostas são construídas a partir dos dados e das regras implementadas.

Isso também significa que o assistente possui limitações: ele não interpreta qualquer pergunta livre como um modelo de linguagem generativo. Sua capacidade depende das intenções e regras implementadas.

O site de apresentação possui uma simulação em JavaScript que permite experimentar consultas, inclusive de chamados fechados. A geração real dos arquivos PDF e Excel está disponível na aplicação Streamlit.

## Funcionalidades

### Dashboard

Apresenta indicadores de quantidade de chamados, violações, atendimentos dentro do SLA e percentual de cumprimento dos chamados encerrados. Também permite filtrar os registros por contrato e período de abertura, visualizar gráficos e consultar uma tabela de atendimentos.

### Calculadora e auditoria de SLA

Permite selecionar um chamado e acompanhar sua meta, tempo líquido consumido e percentual de utilização do prazo. O motor considera horas úteis ou corridas, calendários configuráveis e pausas, evitando descontar duas vezes períodos sobrepostos.

A calculadora também apresenta projeções dos marcos de 25%, 50%, 75% e 100% do prazo, considerando as pausas conhecidas.

### Relatórios gerenciais

Permite gerar relatórios em PDF e Excel com os chamados selecionados. A planilha inclui uma aba de indicadores e uma aba com os registros detalhados. Os arquivos são gerados em memória, sem necessidade de gravar os dados em um banco externo.

### Assistente operacional

Centraliza consultas sobre riscos, violações, resumos e pedidos de relatórios. As respostas utilizam os mesmos registros e indicadores das outras funcionalidades, mantendo uma base comum de análise.

## Tecnologias utilizadas

| Tecnologia | Aplicação no projeto |
| --- | --- |
| Python 3.12 | Linguagem utilizada na lógica, processamento e cálculo de SLA; versão da imagem Docker. |
| Streamlit | Interface web, dashboard, filtros, formulários e chat. |
| Pandas | Organização e apresentação dos dados em tabelas e gráficos. |
| openpyxl | Criação e formatação de planilhas Excel. |
| ReportLab | Geração dos relatórios PDF. |
| datetime e dataclasses | Manipulação de datas, intervalos e configuração dos calendários. |
| re e unicodedata | Identificação de padrões e normalização de texto no assistente. |
| unittest | Testes automatizados das regras de cálculo e relatórios. |
| Docker e Docker Compose | Preparação de um ambiente de execução isolado e reproduzível. |
| HTML, CSS e JavaScript | Site acadêmico de apresentação e demonstração interativa. |
| Git e GitHub | Controle de versões e organização do código. |
| GitHub Pages | Hospedagem da apresentação online. |

## Como o sistema está organizado

Procurei separar a interface, os dados, o processamento e a geração de relatórios para facilitar a manutenção e permitir que as regras de cálculo sejam testadas independentemente da interface.

```text
VERT-Analytics-Academico/
├── demo_v3/
│   ├── app.py          # Interface Streamlit e assistente
│   ├── data.py         # Registros fictícios
│   └── reports.py      # Filtros, indicadores e relatórios
├── sla_core/
│   └── engine.py       # Motor independente de SLA
├── tests/
│   ├── test_demo_v3.py  # Testes de dados e relatórios
│   └── test_engine.py   # Testes do motor de cálculo
├── docs/
│   └── index.html      # Apresentação acadêmica original
├── Dockerfile.demo
├── docker-compose.demo.yml
├── requirements.txt
└── README.md
```

O fluxo começa com a seleção ou consulta de dados. O motor SLA realiza os cálculos, os resultados são organizados pelos módulos de análise e a interface apresenta as informações ao usuário. O assistente e os relatórios utilizam essa mesma base de registros.

## Banco de dados e segurança

No contexto corporativo, o projeto foi desenvolvido para trabalhar com informações de chamados do OTRS, utilizando integração com MySQL. Essa integração não faz parte deste repositório acadêmico.

Para a demonstração, utilizei seis registros sintéticos definidos em Python, com clientes anonimizados, datas, estados, metas e pausas ilustrativas. Não é necessário acessar um banco de dados, utilizar VPN ou fornecer credenciais para executar esta versão.

Também mantive o código acadêmico separado do repositório corporativo. Nenhum registro real de atendimento, configuração de autenticação corporativa ou credencial foi incluído nesta demonstração.

## Como executar

Clone este repositório, caso tenha recebido acesso, e abra um terminal na pasta do projeto. Recomendo Python 3.12.

```bash
python -m pip install -r requirements.txt
python -m streamlit run demo_v3/app.py
```

Abra o endereço indicado pelo Streamlit no terminal. Selecione o período de novembro de 2026 para explorar os registros de demonstração.

Também é possível executar com Docker Desktop:

```bash
docker compose -f docker-compose.demo.yml up --build
```

Acesse http://localhost:8502. Para encerrar:

```bash
docker compose -f docker-compose.demo.yml down
```

Caso queira apenas conhecer o projeto sem instalar nada, utilize a [apresentação online](https://gabrielpereira-03.github.io/VERT-Analytics-Site/).

## Testes e limitações

O projeto inclui testes unitários para horas úteis e corridas, feriados, pausas sobrepostas, projeção de vencimento, filtros, indicadores e geração de arquivos.

```bash
python -m unittest discover -s tests -v
```

A versão acadêmica é uma demonstração offline. Não realiza monitoramento em tempo real, não mantém conversas após o encerramento da sessão e não possui integração com o ambiente corporativo. Os indicadores consideram os registros fictícios e o cumprimento é calculado sobre os chamados encerrados. As metas apresentadas não devem ser utilizadas como referência contratual.

## Considerações finais

Com este projeto, busquei aplicar a programação a um problema do cotidiano profissional. Mais do que criar uma calculadora, a proposta foi transformar dados de atendimento em informações que possam ser consultadas e compreendidas com maior facilidade.

O VERT Analytics reúne conceitos de desenvolvimento de software, processamento de dados, regras de negócio, automação de relatórios e construção de interfaces. O VERT AI representa a evolução dessa proposta, aproximando o usuário das informações por meio de uma interface conversacional.

O projeto continua aberto a melhorias, principalmente na interpretação de perguntas, na validação das regras de negócio e na experiência de utilização.

---

Desenvolvido por Gabriel Pereira — versão acadêmica do VERT Analytics.
