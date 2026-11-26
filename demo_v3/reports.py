"""Geração de relatórios em memória, sem acesso ao OTRS."""
from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle


COLUNAS = [
    ("numero", "Nº Chamado"), ("contrato", "Contrato"), ("severidade", "Severidade"),
    ("estado", "Estado"), ("analista", "Analista"), ("titulo", "Descrição"),
    ("abertura", "Abertura"), ("fim", "Fechamento"),
    ("meta_horas", "Meta (h)"), ("tempo_horas", "Tempo líquido (h)"),
    ("percentual", "Consumo (%)"), ("situacao_sla", "Situação SLA"),
]


def _txt(valor):
    return valor.strftime("%d/%m/%Y %H:%M") if isinstance(valor, datetime) else str(valor if valor is not None else "-")


def filtrar(registros, contrato, inicio, fim):
    """Data de abertura no intervalo, contrato exato ou TODOS."""
    if inicio > fim:
        raise ValueError("A data inicial deve ser anterior ou igual à data final.")
    return [
        r for r in registros if (contrato == "TODOS" or r["contrato"] == contrato)
        and inicio <= r["abertura"].date() <= fim
    ]


def resumo(registros):
    total = len(registros)
    fechados = [r for r in registros if r["estado"] == "Fechado"]
    dentro = sum(r["situacao_sla"] == "Dentro do SLA" for r in fechados)
    violados = sum(r["situacao_sla"] == "Violado" for r in fechados)
    return {
        "total": total, "fechados": len(fechados), "dentro": dentro, "violados": violados,
        "abertos": total - len(fechados),
        "cumprimento": round(dentro * 100 / len(fechados), 1) if fechados else None,
    }


def excel(registros, contrato, inicio, fim):
    wb = Workbook()
    ws = wb.active
    ws.title = "Chamados"
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(COLUNAS))
    ws.cell(1, 1, "VERT Analytics | SLA Engine v3.0 — DEMONSTRAÇÃO")
    ws.cell(1, 1).font = Font(bold=True, size=16, color="FFFFFF")
    ws.cell(1, 1).fill = PatternFill("solid", fgColor="101A3B")
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(COLUNAS))
    ws.cell(2, 1, f"Contrato: {contrato} | {inicio:%d/%m/%Y} a {fim:%d/%m/%Y} | DADOS FICTÍCIOS")
    for col, (_, titulo) in enumerate(COLUNAS, start=1):
        cell = ws.cell(4, col, titulo)
        cell.fill = PatternFill("solid", fgColor="00DE97")
        cell.font = Font(bold=True, color="101A3B")
    for i, reg in enumerate(registros, start=5):
        for j, (campo, _) in enumerate(COLUNAS, start=1):
            cell = ws.cell(i, j, _txt(reg.get(campo)))
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if i % 2 == 0:
                cell.fill = PatternFill("solid", fgColor="EFF8F7")
    larguras = [17, 20, 17, 16, 23, 49, 22, 22, 14, 20, 16, 23]
    for col, tamanho in enumerate(larguras, start=1):
        ws.column_dimensions[get_column_letter(col)].width = tamanho
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:L{max(4, 4 + len(registros))}"
    k = resumo(registros)
    resumo_ws = wb.create_sheet("Indicadores")
    resumo_ws.append(["Indicador", "Valor"])
    for campo, titulo in [("total", "Total"), ("fechados", "Fechados"), ("dentro", "Dentro do SLA"),
                          ("violados", "Violados"), ("abertos", "Em andamento"), ("cumprimento", "Cumprimento (%)")]:
        resumo_ws.append([titulo, k[campo] if k[campo] is not None else "Sem fechados"])
    resumo_ws.column_dimensions["A"].width = 30
    resumo_ws.column_dimensions["B"].width = 22
    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def pdf(registros, contrato, inicio, fim):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=24,
                            rightMargin=24, topMargin=30, bottomMargin=24)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("VertTitle", parent=styles["Heading1"], textColor=colors.HexColor("#101A3B"))
    body = ParagraphStyle("VertBody", parent=styles["Normal"], fontSize=7, leading=9)
    k = resumo(registros)
    indicador = "N/D" if k["cumprimento"] is None else f'{k["cumprimento"]}%'
    story = [
        Paragraph("VERT Analytics | SLA Engine v3.0 — DEMONSTRAÇÃO", title),
        Paragraph(escape(f"Contrato: {contrato} | Período: {inicio:%d/%m/%Y} a {fim:%d/%m/%Y} | DADOS FICTÍCIOS"), body),
        Spacer(1, 12),
        Paragraph(f"Total: {k['total']} | Fechados: {k['fechados']} | Violados: {k['violados']} | Cumprimento: {indicador}", body),
        Spacer(1, 12),
    ]
    campos = [("numero", "Chamado"), ("contrato", "Contrato"), ("severidade", "Severidade"),
              ("analista", "Analista"), ("tempo_horas", "Tempo (h)"), ("situacao_sla", "SLA")]
    linhas = [[Paragraph(escape(cab), body) for _, cab in campos]]
    for reg in registros:
        linhas.append([Paragraph(escape(_txt(reg.get(campo))), body) for campo, _ in campos])
    tabela = LongTable(linhas, colWidths=[95, 120, 100, 150, 85, 145], repeatRows=1)
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#00DE97")),
        ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#CFD8E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F6F7")]),
    ]))
    story.append(tabela)
    doc.build(story)
    return buffer.getvalue()
