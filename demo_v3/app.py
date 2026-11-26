"""VERT Analytics v3.0 — protótipo interativo 100% offline e com dados fictícios.

Execute na raiz do repositório:
  streamlit run demo_v3/app.py
"""
from datetime import date, datetime, timedelta
import re
import unicodedata

import pandas as pd
import streamlit as st

from demo_v3.data import gerar_registros
from demo_v3.reports import excel, filtrar, pdf, resumo
from sla_core.engine import CalendarioSLA, calcular_tempo_liquido, projetar_vencimento


VERDE = "#00DE97"
AZUL = "#101A3B"
CONTRATOS = ("TODOS", "CLIENTE-A", "CLIENTE-B", "CLIENTE-C")

st.set_page_config(page_title="VERT Analytics v3 | Demo", page_icon="📊", layout="wide")
st.markdown(
    """<style>
    .stApp {background:#f4f7fb;color:#101A3B}
    div[data-testid="stMetric"] {background:white;border:1px solid #dce7f0;
        border-top:3px solid #00DE97;padding:16px;border-radius:12px}
    h1,h2,h3 {color:#101A3B}
    .vert-header {background:#101A3B;color:white;padding:21px 25px;border-radius:16px;
        border-left:6px solid #00DE97;margin-bottom:14px}
    .vert-header strong{color:#00DE97}
    .stButton button[kind="primary"]{background:#101A3B;color:white}
    </style>""", unsafe_allow_html=True
)
st.markdown(
    '<div class="vert-header"><strong>VERT Analytics</strong> | SLA Engine v3.0'
    '<div style="font-size:14px;color:#d8e6ec">Dashboard · Auditoria · Chatbot · Relatórios</div></div>',
    unsafe_allow_html=True,
)
st.warning("AMBIENTE DE DEMONSTRAÇÃO — dados 100% fictícios. Sem conexão com OTRS, AD ou banco corporativo.")
pagina = st.sidebar.radio("Navegação", ["Dashboard", "Calculadora", "Assistente", "Relatórios"])
st.sidebar.caption("Identidade visual VERT | Protótipo acadêmico")
contrato = st.sidebar.selectbox("Contrato", CONTRATOS)
inicio = st.sidebar.date_input("Data inicial de abertura", date(2026, 11, 1), format="DD/MM/YYYY")
fim = st.sidebar.date_input("Data final de abertura", date(2026, 11, 30), format="DD/MM/YYYY")
registros = gerar_registros()
try:
    selecionados = filtrar(registros, contrato, inicio, fim)
except ValueError as exc:
    st.error(str(exc))
    st.stop()


def exibir_download(regs, con, d1, d2, prefixo="relatorio"):
    coluna_pdf, coluna_excel = st.columns(2)
    nome = re.sub(r"[^a-zA-Z0-9_-]", "_", con)
    with coluna_pdf:
        st.download_button("📄 Baixar relatório PDF", pdf(regs, con, d1, d2),
                           file_name=f"{prefixo}_{nome}.pdf", mime="application/pdf",
                           use_container_width=True)
    with coluna_excel:
        st.download_button("📗 Baixar relatório Excel", excel(regs, con, d1, d2),
                           file_name=f"{prefixo}_{nome}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True)


def formatar_tabela(rows):
    return pd.DataFrame([{
        "Chamado": r["numero"], "Contrato": r["contrato"],
        "Descrição": r["titulo"], "Severidade": r["severidade"],
        "Analista": r["analista"], "Status": r["estado"],
        "Tempo (h)": r["tempo_horas"], "Meta (h)": r["meta_horas"],
        "Consumo (%)": r["percentual"], "Situação": r["situacao_sla"],
    } for r in rows])


def sem_acentos(s):
    return "".join(ch for ch in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(ch) != "Mn")


def interpretar_pedido(texto):
    """Extrai formato, contrato e datas; não executa ações arbitrárias."""
    normal = sem_acentos(texto)
    con = next((c for c in CONTRATOS[1:] if sem_acentos(c) in normal), None)
    if con is None and "cliente-a" in normal:
        con = "CLIENTE-A"
    if con is None and "cliente-b" in normal:
        con = "CLIENTE-B"
    if con is None and "cliente-c" in normal:
        con = "CLIENTE-C"
    con = con or contrato
    datas = re.findall(r"\b(\d{2}/\d{2}/\d{4})\b", texto)
    di, df = inicio, fim
    if len(datas) == 2:
        try:
            di, df = [datetime.strptime(s, "%d/%m/%Y").date() for s in datas]
        except ValueError:
            return None, "Data inválida. Use DD/MM/AAAA."
    elif "mes passado" in normal:
        hoje = date.today()
        primeiro_mes = hoje.replace(day=1)
        df = primeiro_mes - timedelta(days=1)
        di = df.replace(day=1)
    elif "mes atual" in normal:
        hoje = date.today()
        di, df = hoje.replace(day=1), hoje
    if di > df:
        return None, "Data inicial maior que a final."
    formato = "excel" if any(x in normal for x in ("excel", "xlsx", "planilha")) else "pdf"
    return (con, di, df, formato), None


def painel_kpis(rows):
    k = resumo(rows)
    a, b, c, d = st.columns(4)
    a.metric("Chamados", k["total"])
    b.metric("Dentro do SLA", k["dentro"])
    c.metric("Violações", k["violados"])
    d.metric("Cumprimento (fechados)", "N/D" if k["cumprimento"] is None else f'{k["cumprimento"]}%')


if pagina == "Dashboard":
    st.subheader("Visão executiva")
    painel_kpis(selecionados)
    if selecionados:
        df = formatar_tabela(selecionados)
        a, b = st.columns(2)
        with a:
            st.markdown("**Distribuição por contrato**")
            st.bar_chart(df["Contrato"].value_counts())
        with b:
            st.markdown("**Situação dos chamados**")
            st.bar_chart(df["Situação"].value_counts())
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum chamado sintético encontrado neste período.")

elif pagina == "Calculadora":
    st.subheader("Auditoria de chamado")
    chamados = [r["numero"] for r in selecionados]
    if not chamados:
        st.info("Nenhum chamado encontrado nos filtros atuais.")
    else:
        numero = st.selectbox("Chamado fictício", chamados)
        chamado = next(r for r in selecionados if r["numero"] == numero)
        st.markdown(f"**{chamado['titulo']}** | {chamado['contrato']} | {chamado['severidade']}")
        a, b, c = st.columns(3)
        a.metric("Meta SLA", f"{chamado['meta_horas']} h")
        b.metric("Tempo líquido", f"{chamado['tempo_horas']} h")
        c.metric("Consumo", f"{chamado['percentual']}%")
        st.progress(min(1.0, chamado["percentual"] / 100))
        st.write(f"**Situação:** {chamado['situacao_sla']}")
        if chamado["fim"] is None:
            st.caption("Simulação com data de referência fixa; não representa monitoramento em tempo real.")
        cal = CalendarioSLA(horas_corridas=chamado["calendario"] == "CORRIDO")
        try:
            marcos = {
                f"{m}%": projetar_vencimento(
                    chamado["abertura"], timedelta(hours=chamado["meta_horas"] * m / 100),
                    cal, chamado["pausas"]).strftime("%d/%m/%Y %H:%M")
                for m in (25, 50, 75, 100)
            }
            st.markdown("**Marcos projetados**")
            st.table(pd.DataFrame(list(marcos.items()), columns=["Marco", "Data/hora"]))
        except ValueError as exc:
            st.error(f"Não foi possível projetar: {exc}")
        st.caption("Projeção demonstrativa: usa apenas pausas conhecidas e calendário fictício.")

elif pagina == "Relatórios":
    st.subheader("Relatórios gerenciais")
    painel_kpis(selecionados)
    st.caption("Filtro por data de abertura. O cálculo é sintético e não auditado para contratos reais.")
    if selecionados:
        st.dataframe(formatar_tabela(selecionados), use_container_width=True, hide_index=True)
    exibir_download(selecionados, contrato, inicio, fim)

else:
    st.subheader("VERT AI — assistente operacional demonstrativo")
    st.caption("Assistente local baseado em regras. Dados fictícios. Experimente: quais chamados estão em risco? Ou gere um Excel da CLIENTE-A.")
    if "demo_chat" not in st.session_state:
        st.session_state.demo_chat = []
    for idx, msg in enumerate(st.session_state.demo_chat):
        with st.chat_message(msg["role"]):
            st.markdown(msg["text"])
            if msg.get("report"):
                con, di, df, fmt = msg["report"]
                rows = filtrar(registros, con, di, df)
                if fmt == "excel":
                    st.download_button("📗 Baixar Excel", excel(rows, con, di, df),
                        file_name=f"VERT_demo_{idx}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"xlsx_{idx}")
                else:
                    st.download_button("📄 Baixar PDF", pdf(rows, con, di, df),
                        file_name=f"VERT_demo_{idx}.pdf", mime="application/pdf", key=f"pdf_{idx}")

    if prompt := st.chat_input("Peça um relatório por contrato e período..."):
        st.session_state.demo_chat.append({"role": "user", "text": prompt})
        normal = sem_acentos(prompt)
        if any(v in normal for v in ("risco","violacao","violacoes","violados","resumo","compare","comparar")) and not any(v in normal for v in ("relatorio","excel","planilha","pdf")):
            pedido, erro = interpretar_pedido(prompt)
            if erro:
                resposta={"role":"assistant","text":erro}
            else:
                con,di,df,_=pedido
                rows=filtrar(registros,con,di,df)
                k=resumo(rows)
                risco="risco" in normal
                violacao=any(v in normal for v in ("violacao","violacoes","violados"))
                lista=[r for r in rows if 75<=r["percentual"]<=100 and r["fim"] is None] if risco else [r for r in rows if r["percentual"]>100] if violacao else []
                lista=sorted(lista,key=lambda r:r["percentual"],reverse=True)
                detalhes="\n".join(f"- {r['numero']} | {r['contrato']} | {r['percentual']}%" for r in lista[:10])
                resposta={"role":"assistant","text":f"**DEMONSTRAÇÃO FICTÍCIA | {con}** — {k['total']} chamados, {k['violados']} violações. Cumprimento (encerrados): {k['cumprimento'] if k['cumprimento'] is not None else 'N/D'}%.\n\n"+(f"Encontrados: {len(lista)} (até 10 exibidos).\n"+detalhes if risco or violacao else "Consulte os filtros ou peça um relatório.")}
        elif not any(v in normal for v in ("relatorio", "excel", "planilha", "pdf")):
            resposta = {"role": "assistant", "text":
                "Posso gerar relatórios PDF ou Excel com dados de demonstração. "
                "Exemplo: 'Relatório CLIENTE-A de 01/11/2026 a 19/11/2026 em Excel'."}
        else:
            pedido, erro = interpretar_pedido(prompt)
            if erro:
                resposta = {"role": "assistant", "text": f"⚠️ {erro}"}
            else:
                con, di, df, fmt = pedido
                rows = filtrar(registros, con, di, df)
                k = resumo(rows)
                resposta = {"role": "assistant",
                    "text": f"📊 **Relatório {con}** | {di:%d/%m/%Y}–{df:%d/%m/%Y} "
                            f"| Chamados: **{k['total']}**, violações: **{k['violados']}**. "
                            f"Arquivo **{fmt.upper()}** disponível abaixo. "
                            "Todos os registros são fictícios.",
                    "report": pedido}
        st.session_state.demo_chat.append(resposta)
        st.rerun()
