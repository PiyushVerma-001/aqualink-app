"""Generate the Finance Data Lab submission PDF.

The document deliberately distinguishes audited/public facts from classroom
analytics that require licensed Bloomberg, ProwessDX, or ACE MF exports.
"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Iterable, Sequence

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.graphics.shapes import Drawing, Line, PolyLine, Rect, String


OUT = Path(__file__).with_name("FDL_Britannia_Food_Agro_Report.pdf")
PAGE = landscape(A4)
W, H = PAGE

BG = colors.HexColor("#080a09")
PANEL = colors.HexColor("#111411")
PANEL_2 = colors.HexColor("#171a17")
GRID = colors.HexColor("#343934")
ORANGE = colors.HexColor("#ff9f1c")
GREEN = colors.HexColor("#36d399")
RED = colors.HexColor("#ff6666")
BLUE = colors.HexColor("#53a7ff")
TEXT = colors.HexColor("#f0f2ed")
MUTED = colors.HexColor("#9aa198")
DIM = colors.HexColor("#666d66")
WHITE = colors.white


def register_fonts() -> tuple[str, str]:
    mono = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    sans = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if os.path.exists(mono):
        pdfmetrics.registerFont(TTFont("TerminalMono", mono))
        pdfmetrics.registerFont(TTFont("TerminalSans", sans))
        return "TerminalMono", "TerminalSans"
    return "Courier", "Helvetica"


MONO, SANS = register_fonts()


class NumberedCanvasMixin:
    pass


def page_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#0d100e"))
    canvas.rect(0, H - 13 * mm, W, 13 * mm, fill=1, stroke=0)
    canvas.setStrokeColor(GRID)
    canvas.line(0, H - 13 * mm, W, H - 13 * mm)
    canvas.setFont(MONO, 7)
    canvas.setFillColor(ORANGE)
    canvas.drawString(12 * mm, H - 8.5 * mm, "MERIDIAN // FINANCE DATA LAB")
    canvas.setFillColor(MUTED)
    canvas.drawRightString(W - 12 * mm, H - 8.5 * mm, "FOOD & AGRO PRODUCTS  |  27 SEP 2026")
    canvas.setStrokeColor(GRID)
    canvas.line(12 * mm, 9 * mm, W - 12 * mm, 9 * mm)
    canvas.setFont(MONO, 6.5)
    canvas.setFillColor(DIM)
    canvas.drawString(12 * mm, 5.3 * mm, "ACADEMIC RESEARCH // NOT INVESTMENT ADVICE")
    canvas.drawRightString(W - 12 * mm, 5.3 * mm, f"PAGE {doc.page:02d}")
    canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="Kicker",
        fontName=MONO,
        fontSize=7,
        leading=9,
        textColor=ORANGE,
        spaceAfter=2 * mm,
        uppercase=True,
    )
)
styles.add(
    ParagraphStyle(
        name="TitleTerminal",
        fontName=SANS,
        fontSize=25,
        leading=28,
        textColor=TEXT,
        spaceAfter=2.2 * mm,
    )
)
styles.add(
    ParagraphStyle(
        name="SubTitleTerminal",
        fontName=MONO,
        fontSize=8.5,
        leading=12,
        textColor=MUTED,
        spaceAfter=4 * mm,
    )
)
styles.add(
    ParagraphStyle(
        name="Section",
        fontName=MONO,
        fontSize=10,
        leading=12,
        textColor=TEXT,
        borderColor=GRID,
        borderWidth=0.5,
        borderPadding=(2.2 * mm, 2.5 * mm, 2.2 * mm, 2.5 * mm),
        backColor=PANEL_2,
        spaceAfter=2.5 * mm,
    )
)
styles.add(
    ParagraphStyle(
        name="BodyT",
        fontName=SANS,
        fontSize=7.5,
        leading=10.4,
        textColor=TEXT,
        spaceAfter=1.7 * mm,
    )
)
styles.add(
    ParagraphStyle(
        name="SmallT",
        fontName=MONO,
        fontSize=6.2,
        leading=8.2,
        textColor=MUTED,
    )
)
styles.add(
    ParagraphStyle(
        name="Callout",
        fontName=SANS,
        fontSize=8,
        leading=11,
        textColor=TEXT,
        leftIndent=3 * mm,
        borderColor=ORANGE,
        borderWidth=0,
        borderLeftWidth=2,
        borderPadding=2.5 * mm,
        backColor=PANEL,
    )
)
styles.add(
    ParagraphStyle(
        name="Metric",
        fontName=MONO,
        fontSize=15,
        leading=17,
        textColor=TEXT,
        alignment=TA_CENTER,
    )
)
styles.add(
    ParagraphStyle(
        name="MetricLabel",
        fontName=MONO,
        fontSize=5.8,
        leading=7,
        textColor=MUTED,
        alignment=TA_CENTER,
    )
)
styles.add(
    ParagraphStyle(
        name="Foot",
        fontName=MONO,
        fontSize=5.5,
        leading=7.2,
        textColor=DIM,
    )
)


def p(text: str, style: str = "BodyT") -> Paragraph:
    return Paragraph(text, styles[style])


def title(question: str, heading: str, subtitle: str):
    return [
        p(question, "Kicker"),
        p(heading, "TitleTerminal"),
        p(subtitle, "SubTitleTerminal"),
    ]


def section(text: str) -> Paragraph:
    return p(text, "Section")


def bullet(items: Iterable[str]) -> list:
    return [p(f'<font color="#ff9f1c">›</font> {item}') for item in items]


def terminal_table(
    data: Sequence[Sequence[object]],
    widths: Sequence[float] | None = None,
    font_size: float = 6.5,
    row_bgs: bool = True,
):
    prepared = []
    for r, row in enumerate(data):
        prepared.append(
            [
                cell
                if isinstance(cell, (Paragraph, Drawing))
                else p(str(cell), "SmallT")
                for cell in row
            ]
        )
    t = Table(prepared, colWidths=widths, repeatRows=1, hAlign="LEFT")
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), PANEL_2),
        ("TEXTCOLOR", (0, 0), (-1, 0), ORANGE),
        ("FONTNAME", (0, 0), (-1, 0), MONO),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 1.7 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.7 * mm),
    ]
    if row_bgs:
        for r in range(1, len(data)):
            if r % 2 == 0:
                commands.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#0d100e")))
    t.setStyle(TableStyle(commands))
    return t


def metric_strip(items: Sequence[tuple[str, str, str]]):
    cells = []
    for label, value, tone in items:
        color = {"green": GREEN, "red": RED, "orange": ORANGE}.get(tone, TEXT)
        cells.append(
            Table(
                [
                    [p(label, "MetricLabel")],
                    [Paragraph(value, ParagraphStyle("mv", parent=styles["Metric"], textColor=color))],
                ],
                colWidths=[(W - 28 * mm) / len(items)],
            )
        )
    outer = Table([cells])
    outer.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PANEL),
                ("BOX", (0, 0), (-1, -1), 0.5, GRID),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, GRID),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ]
        )
    )
    return outer


def line_chart(
    series: Sequence[float],
    labels: Sequence[str],
    width: float = 350,
    height: float = 105,
    color=ORANGE,
    title_text: str = "",
):
    d = Drawing(width, height)
    d.add(Rect(0, 0, width, height, fillColor=PANEL, strokeColor=GRID, strokeWidth=0.5))
    pad_l, pad_r, pad_t, pad_b = 33, 12, 17, 19
    cw, ch = width - pad_l - pad_r, height - pad_t - pad_b
    lo, hi = min(series), max(series)
    span = hi - lo or 1
    for i in range(5):
        y = pad_b + ch * i / 4
        d.add(Line(pad_l, y, width - pad_r, y, strokeColor=GRID, strokeWidth=0.4))
        val = lo + span * i / 4
        d.add(String(3, y - 2.3, f"{val:.0f}", fontName=MONO, fontSize=5, fillColor=DIM))
    pts = []
    for i, value in enumerate(series):
        x = pad_l + cw * i / max(1, len(series) - 1)
        y = pad_b + (value - lo) / span * ch
        pts.extend([x, y])
    d.add(PolyLine(pts, strokeColor=color, strokeWidth=1.7, fillColor=None))
    for i, lab in enumerate(labels):
        x = pad_l + cw * i / max(1, len(labels) - 1)
        d.add(String(x - 9, 6, lab, fontName=MONO, fontSize=5, fillColor=DIM))
    if title_text:
        d.add(String(pad_l, height - 11, title_text, fontName=MONO, fontSize=6, fillColor=MUTED))
    return d


def bar_chart(
    labels: Sequence[str],
    values: Sequence[float],
    width: float = 330,
    height: float = 105,
    color=GREEN,
    suffix: str = "%",
):
    d = Drawing(width, height)
    d.add(Rect(0, 0, width, height, fillColor=PANEL, strokeColor=GRID, strokeWidth=0.5))
    maxv = max(abs(v) for v in values) or 1
    left, right = 55, 15
    usable = width - left - right
    row_h = (height - 12) / len(values)
    zero = left + usable * 0.42
    d.add(Line(zero, 5, zero, height - 5, strokeColor=DIM, strokeWidth=0.5))
    for i, (lab, value) in enumerate(zip(labels, values)):
        y = height - (i + 1) * row_h + 4
        d.add(String(5, y + 2, lab[:13], fontName=MONO, fontSize=5.2, fillColor=MUTED))
        magnitude = abs(value) / maxv * usable * 0.52
        if value >= 0:
            x = zero
            fill = color
        else:
            x = zero - magnitude
            fill = RED
        d.add(Rect(x, y, magnitude, row_h * 0.48, fillColor=fill, strokeColor=None))
        d.add(
            String(
                x + magnitude + 3 if value >= 0 else x - 30,
                y + 1,
                f"{value:+.1f}{suffix}",
                fontName=MONO,
                fontSize=5.2,
                fillColor=fill,
            )
        )
    return d


def two_col(left, right, widths=(0.50, 0.50)):
    total = W - 28 * mm
    t = Table([[left, right]], colWidths=[total * widths[0], total * widths[1]])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (0, -1), 0),
                ("RIGHTPADDING", (0, 0), (0, -1), 2.2 * mm),
                ("LEFTPADDING", (1, 0), (1, -1), 2.2 * mm),
                ("RIGHTPADDING", (1, 0), (1, -1), 0),
            ]
        )
    )
    return t


def source_note(text: str):
    return p(f"<b>SOURCE / METHOD:</b> {text}", "Foot")


def build_story():
    story = []

    # Q1, page 1 of 5
    story += title(
        "Q1 // STOCK ANALYST REPORT // PAGE 1 OF 5",
        "Britannia Industries Ltd.",
        "Food & agro-based products  |  Bottom-up analyst report  |  NSE: BRITANNIA  |  FY2024–25",
    )
    story.append(
        metric_strip(
            [
                ("CONSOL. REVENUE", "₹17,943cr", "orange"),
                ("OPERATING PROFIT", "₹2,874cr", "green"),
                ("PAT / OWNER", "₹2,179cr", "green"),
                ("OP. MARGIN", "16.0%", "white"),
                ("PROMOTER HOLDING", "50.55%", "white"),
            ]
        )
    )
    story.append(Spacer(1, 3 * mm))
    left = [
        section("INVESTMENT VIEW"),
        p(
            "<b>Quality compounder, but input inflation determines the entry point.</b> "
            "Britannia combines national distribution, premium brand equity and high cash conversion. "
            "FY25 consolidated revenue grew 7.0%, while operating profit was nearly flat—evidence that "
            "wheat, palm oil, cocoa and dairy inflation can delay margin recovery."
        ),
        p(
            "<b>Base case:</b> high-single-digit revenue growth, gradual gross-margin normalization and "
            "continued premiumization. <b>Key debate:</b> whether price/mix can offset commodity costs "
            "without impairing rural volumes."
        ),
        p(
            "Analyst stance: <font color='#36d399'><b>WATCH / ACCUMULATE ON VALUATION COMPRESSION</b></font>. "
            "No target price is stated because the licensed adjusted price series was not supplied."
        ),
        Spacer(1, 2 * mm),
        section("CATALYSTS / RISKS"),
        terminal_table(
            [
                ["CATALYST", "WHY IT MATTERS"],
                ["Rural real-income recovery", "Volume growth and pack upgrades"],
                ["Commodity deflation", "Fast gross-margin transmission"],
                ["Adjacent categories", "Higher addressable market"],
                ["Direct distribution", "Lower leakage; better assortment"],
                ["Cocoa / palm spike", "Margin and demand elasticity risk"],
                ["Intense regional competition", "Trade spend and price pressure"],
            ],
            widths=[55 * mm, 74 * mm],
        ),
    ]
    right = [
        section("TOP-DOWN DRIVER MAP"),
        terminal_table(
            [
                ["DRIVER", "TRANSMISSION", "SIGNAL"],
                ["Food inflation", "Input cost / wallet", "High"],
                ["Rural wages", "Biscuit volume", "Improving"],
                ["Monsoon", "Agri income + wheat", "Monitor"],
                ["USD/INR", "Palm/cocoa imports", "Adverse if ↑"],
                ["Crude/freight", "Packaging/logistics", "Moderate"],
                ["Policy / GST", "Demand + formalization", "Supportive"],
            ],
            widths=[37 * mm, 53 * mm, 30 * mm],
        ),
        Spacer(1, 3 * mm),
        section("INDUSTRY SNAPSHOT"),
        metric_strip(
            [
                ("9Y GROWTH", "6.55%", "orange"),
                ("FY24 GVA", "₹2.24L cr", "green"),
                ("PROCESSED / AGRI EXPORTS", "20.4%", "white"),
            ]
        ),
        Spacer(1, 3 * mm),
        p(
            "India's processed-food ecosystem benefits from abundant agricultural inputs, formal retail, "
            "e-commerce, cold-chain investment and the ₹10,900 crore PLI scheme. Organized players gain "
            "share from compliance, distribution depth and consumer trust."
        ),
        source_note(
            "Britannia FY25 Annual Report; MoFPI Annual Report 2024–25; PIB food-processing releases. "
            "Currency figures rounded."
        ),
    ]
    story.append(two_col(left, right, (0.52, 0.48)))
    story.append(PageBreak())

    # Q1, page 2
    story += title(
        "Q1 // STOCK ANALYST REPORT // PAGE 2 OF 5",
        "Industry structure & strategic position",
        "Indian packaged food: structural growth with commodity-sensitive economics",
    )
    swot = [
        [
            section("STRENGTHS"),
            section("WEAKNESSES"),
            section("OPPORTUNITIES"),
            section("THREATS"),
        ],
        [
            p("• Trusted national brands<br/>• Deep general-trade reach<br/>• Strong biscuit scale<br/>• Cash-generative model"),
            p("• Biscuit concentration<br/>• Premium valuation history<br/>• Commodity-linked margins<br/>• Rural price sensitivity"),
            p("• Dairy / bakery adjacencies<br/>• Premium snacking<br/>• Rural distribution<br/>• Exports and digital channels"),
            p("• Regional brands<br/>• Health regulation<br/>• Climate-led crop shocks<br/>• Private-label competition"),
        ],
    ]
    story.append(terminal_table(swot, widths=[67 * mm] * 4))
    story.append(Spacer(1, 3 * mm))
    left = [
        section("PORTER / DATA WORTH REPORTING"),
        terminal_table(
            [
                ["FORCE", "ASSESSMENT", "KPI"],
                ["Rivalry", "High", "Volume share; ad spend"],
                ["Buyer power", "Low retail / high modern", "Trade spend"],
                ["Supplier power", "Cyclical", "Wheat, palm, cocoa"],
                ["New entrants", "Moderate", "Distribution reach"],
                ["Substitution", "High", "At-home / local snacks"],
            ],
            widths=[37 * mm, 43 * mm, 53 * mm],
        ),
        Spacer(1, 3 * mm),
        section("SECTOR MONITOR"),
        bar_chart(
            ["Distribution", "Brand", "Pricing", "Input cost", "Innovation", "Regulation"],
            [4.7, 4.5, 3.8, -4.2, 3.4, -2.1],
            width=380,
            height=112,
            suffix="",
        ),
    ]
    right = [
        section("COMPETITIVE SCORECARD // 1–5"),
        terminal_table(
            [
                ["COMPANY", "BRAND", "REACH", "MARGIN", "DIVERSITY"],
                ["Britannia", "5.0", "5.0", "4.2", "3.3"],
                ["Nestlé India", "5.0", "4.6", "4.8", "4.3"],
                ["Tata Consumer", "4.5", "4.4", "3.6", "4.7"],
                ["Mrs Bectors", "3.4", "3.1", "3.7", "2.8"],
                ["Bikaji Foods", "4.0", "3.7", "3.5", "3.1"],
            ],
            widths=[49 * mm, 24 * mm, 24 * mm, 24 * mm, 28 * mm],
        ),
        Spacer(1, 3 * mm),
        p(
            "<b>Interpretation.</b> Britannia's moat is strongest where brand and physical reach reinforce "
            "one another. Product diversification trails broader FMCG peers; this is both the largest "
            "risk and clearest reinvestment runway."
        ),
        p(
            "<b>What changes the thesis:</b> sustained volume share losses, structural deterioration in "
            "cash conversion, promoter pledging, or debt-funded diversification outside core capabilities."
        ),
        source_note("Analyst scoring framework; sector facts from MoFPI/PIB. Scores are qualitative research judgments."),
    ]
    story.append(two_col(left, right))
    story.append(PageBreak())

    # Q1, page 3
    story += title(
        "Q1 // STOCK ANALYST REPORT // PAGE 3 OF 5",
        "Financial trend & ratio analysis",
        "Consolidated research worksheet  |  ₹ crore unless stated",
    )
    financials = [
        ["YEAR", "REVENUE", "OPER. PROFIT", "PAT", "OPM", "PAT MARGIN", "ROCE*", "NET DEBT/EBITDA*"],
        ["FY21", "13,136", "2,453", "1,864", "18.7%", "14.2%", "34%", "0.35x"],
        ["FY22", "13,371", "2,086", "1,525", "15.6%", "11.4%", "29%", "0.48x"],
        ["FY23", "16,301", "3,036", "2,322", "18.6%", "14.2%", "38%", "0.31x"],
        ["FY24", "16,769", "2,869", "2,134", "17.1%", "12.7%", "34%", "0.26x"],
        ["FY25", "17,943", "2,874", "2,179", "16.0%", "12.1%", "32%", "0.22x"],
    ]
    story.append(terminal_table(financials, widths=[24 * mm, 34 * mm, 36 * mm, 30 * mm, 28 * mm, 32 * mm, 27 * mm, 40 * mm]))
    story.append(Spacer(1, 3 * mm))
    story.append(
        two_col(
            [
                line_chart(
                    [13136, 13371, 16301, 16769, 17943],
                    ["FY21", "FY22", "FY23", "FY24", "FY25"],
                    width=385,
                    height=120,
                    title_text="CONSOLIDATED REVENUE // ₹CR",
                ),
                Spacer(1, 2 * mm),
                p(
                    "<b>Trend:</b> five-year revenue CAGR is approximately 8.1%. Growth was not linear: "
                    "FY22 margins compressed, FY23 rebounded, and FY25 showed top-line resilience but "
                    "limited operating-profit growth."
                ),
            ],
            [
                line_chart(
                    [18.7, 15.6, 18.6, 17.1, 16.0],
                    ["FY21", "FY22", "FY23", "FY24", "FY25"],
                    width=385,
                    height=120,
                    color=GREEN,
                    title_text="OPERATING MARGIN // %",
                ),
                Spacer(1, 2 * mm),
                p(
                    "<b>Balance-sheet view:</b> leverage appears manageable and interest coverage remains "
                    "strong. High dividend payout supports capital discipline, though it lowers retained "
                    "cash available for large inorganic growth."
                ),
            ],
        )
    )
    story.append(Spacer(1, 2 * mm))
    story.append(
        source_note(
            "FY25/FY24 audited figures from Britannia FY25 Annual Report. Earlier years and starred ratios "
            "are normalized research-workbook values assembled from annual-report series; reconcile to "
            "ProwessDX before graded submission."
        )
    )
    story.append(PageBreak())

    # Q1, page 4
    story += title(
        "Q1 // STOCK ANALYST REPORT // PAGE 4 OF 5",
        "Debt, cash flow & contingent exposures",
        "The balance-sheet questions that headline multiples can hide",
    )
    debt = [
        ["ITEM", "FY25 RESEARCH VIEW", "ANALYST INTERPRETATION"],
        ["Bank borrowings", "Limited / working-capital led", "No structural dependence"],
        ["NCD / bonds", "5.5% NCD series disclosed", "Low-cost legacy funding"],
        ["Commercial paper", "No material balance identified", "Confirm in ProwessDX"],
        ["Lease liabilities", "Included in adjusted debt", "Treat as operating financing"],
        ["Bank guarantees / LC", "₹49.69cr", "Down from ₹124.00cr"],
        ["Claims not acknowledged", "₹12.22cr", "Low vs operating profit"],
        ["Material RPT", "None under Sec. 188(1)", "Ordinary course / arm's length"],
        ["Inter-corporate deposits", "No material ICD flagged", "Verify Note 43 extraction"],
    ]
    story.append(terminal_table(debt, widths=[55 * mm, 75 * mm, 137 * mm]))
    story.append(Spacer(1, 3 * mm))
    story.append(
        metric_strip(
            [
                ("FY24 CFO", "₹2,573cr", "green"),
                ("FY24 CAPEX", "₹562cr", "orange"),
                ("FY24 FCFF PROXY", "₹1,850cr", "green"),
                ("INTEREST COVER*", ">15x", "green"),
                ("CONTINGENT / OP", "2.2%", "white"),
            ]
        )
    )
    story.append(Spacer(1, 3 * mm))
    left = [
        section("FCFF BRIDGE // PROXY"),
        terminal_table(
            [
                ["STEP", "₹CR"],
                ["Cash flow from operations", "2,573"],
                ["Less: gross capex", "(562)"],
                ["Add: after-tax interest proxy", "55"],
                ["Less: normalized WC adjustment", "(216)"],
                ["Estimated FCFF", "1,850"],
            ],
            widths=[92 * mm, 37 * mm],
        ),
    ]
    right = [
        section("READ-THROUGH"),
        *bullet(
            [
                "Cash generation materially exceeds maintenance investment.",
                "Contingent liabilities are not large relative to annual operating profit.",
                "Arm's-length RPT disclosure is positive; recurring royalty, purchase and group balances still warrant annual tracking.",
                "Exact debt split, finance cost and ICD balances must be exported directly from ProwessDX for auditability.",
            ]
        ),
        source_note(
            "FY24 cash-flow values from public company disclosures; contingent/RPT data from FY25 Annual Report. "
            "FCFF and interest coverage are analyst proxies, not company-reported KPIs."
        ),
    ]
    story.append(two_col(left, right))
    story.append(PageBreak())

    # Q1, page 5
    story += title(
        "Q1 // STOCK ANALYST REPORT // PAGE 5 OF 5",
        "Price, valuation, actions & governance",
        "A disciplined conclusion—and the data gaps that must not be disguised",
    )
    story.append(
        two_col(
            [
                section("FIVE-YEAR PRICE FRAME"),
                line_chart(
                    [100, 108, 96, 121, 132, 124, 148, 143, 167, 159, 181, 174],
                    ["21", "", "22", "", "23", "", "24", "", "25", "", "26", ""],
                    width=390,
                    height=128,
                    title_text="TOTAL-RETURN INDEX // ILLUSTRATIVE, BASE 100",
                ),
                Spacer(1, 2 * mm),
                p(
                    "<b>Adjusted vs unadjusted:</b> the adjusted series should reinvest dividends and "
                    "reflect splits/bonuses. Britannia's ₹75 FY25 final dividend is economically meaningful; "
                    "using only unadjusted closes understates shareholder return."
                ),
            ],
            [
                section("VALUATION LENS"),
                terminal_table(
                    [
                        ["METRIC", "USE", "CURRENT READ"],
                        ["P/E", "Quality / duration", "Premium to market"],
                        ["EV/EBITDA", "Capital structure neutral", "Premium to staples"],
                        ["FCF yield", "Cash valuation", "Key entry signal"],
                        ["PEG", "Price vs growth", "Demanding if volume slows"],
                        ["Dividend yield", "Carry", "Modest; high payout"],
                    ],
                    widths=[38 * mm, 58 * mm, 45 * mm],
                ),
                Spacer(1, 3 * mm),
                section("CORPORATE ACTION / OWNERSHIP"),
                terminal_table(
                    [
                        ["ITEM", "FY25 / MAR-25"],
                        ["Final dividend", "₹75 per share"],
                        ["Promoter", "50.55%; no pledge"],
                        ["FII", "15.72%"],
                        ["DII", "18.26%"],
                        ["Public / other", "15.47%"],
                    ],
                    widths=[65 * mm, 76 * mm],
                ),
            ],
        )
    )
    story.append(Spacer(1, 3 * mm))
    story.append(
        p(
            "<b>Governance conclusion.</b> Stable promoter ownership and zero pledge are constructive. "
            "Board oversight, related-party transactions, succession, remuneration and capital allocation "
            "remain the decisive qualitative checks. <b>Recommendation discipline:</b> do not publish a "
            "precise target price until licensed adjusted prices and consensus estimates are refreshed."
        )
    )
    story.append(
        source_note(
            "Britannia FY25 Annual Report; NSE shareholding filings; public ownership aggregators. "
            "The chart is an explicitly illustrative index—not a Bloomberg export."
        )
    )
    story.append(PageBreak())

    # Q2
    story += title(
        "Q2 // INTERNATIONAL PEER // PAGE 1 OF 2",
        "Mondelēz International",
        "Global snacking peer  |  NASDAQ: MDLZ  |  FY2025",
    )
    story.append(
        metric_strip(
            [
                ("NET REVENUE", "$38.5bn", "orange"),
                ("OPERATING INCOME", "$3.55bn", "white"),
                ("OPERATING MARGIN", "9.2%", "red"),
                ("OPERATING CASH FLOW", "$4.5bn", "green"),
                ("FREE CASH FLOW", "$3.2bn", "green"),
            ]
        )
    )
    story.append(Spacer(1, 3 * mm))
    story.append(
        two_col(
            [
                section("FINANCIAL PERFORMANCE"),
                terminal_table(
                    [
                        ["KPI", "FY25", "YOY / READ"],
                        ["Net revenue", "$38.5bn", "+5.8% reported"],
                        ["Organic revenue", "—", "+4.3%"],
                        ["Volume / mix", "—", "-3.7%"],
                        ["Gross margin", "28.4%", "-10.7ppt"],
                        ["Operating margin", "9.2%", "-8.2ppt"],
                        ["Diluted EPS", "$1.89", "-44.7%"],
                        ["Adjusted EPS", "$2.92", "-14.6% CC"],
                    ],
                    widths=[54 * mm, 34 * mm, 48 * mm],
                ),
                Spacer(1, 2 * mm),
                p(
                    "The cocoa shock created a sharp price/volume trade-off: strong reported revenue "
                    "coexisted with lower volume/mix and materially weaker margins. This is a useful stress "
                    "case for Britannia's commodity-risk framework."
                ),
            ],
            [
                section("PEER COMPARISON"),
                terminal_table(
                    [
                        ["DIMENSION", "BRITANNIA", "MONDELĒZ"],
                        ["Geography", "India-led", "150+ countries"],
                        ["Core", "Biscuits / bakery", "Biscuits / chocolate"],
                        ["FY25 growth", "7.0%", "5.8%"],
                        ["Operating margin", "16.0%", "9.2% GAAP"],
                        ["Commodity risk", "Wheat / palm / dairy", "Cocoa / sugar"],
                        ["Currency risk", "Import INR", "Global translation"],
                        ["FCF", "Strong conversion", "$3.2bn"],
                    ],
                    widths=[47 * mm, 50 * mm, 50 * mm],
                ),
                Spacer(1, 2 * mm),
                p(
                    "<b>Read:</b> Britannia has superior current operating margin but less geographic "
                    "diversification. Mondelēz has greater global scale and category breadth, yet its 2025 "
                    "results show that even scale cannot fully neutralize a commodity super-spike."
                ),
            ],
        )
    )
    story.append(source_note("Mondelēz FY2025 10-K and FY2025 results release; Britannia FY25 Annual Report."))
    story.append(PageBreak())

    story += title(
        "Q2 // INTERNATIONAL PEER // PAGE 2 OF 2",
        "ESG & market-performance frame",
        "Operational sustainability is financially material in cocoa, packaging and energy",
    )
    story.append(
        two_col(
            [
                section("ESG SCOREBOARD"),
                terminal_table(
                    [
                        ["TOPIC", "DISCLOSED PROGRESS", "ANALYST VIEW"],
                        ["GHG value chain", "-21% vs 2018", "Material progress"],
                        ["Renewable power", "Program expanding", "Cost + carbon"],
                        ["Packaging", "Virgin plastic focus", "Execution risk"],
                        ["Cocoa sourcing", "Cocoa Life / CLMRS", "Core license to operate"],
                        ["Pay equity", "<1% gender gap", "Positive disclosure"],
                        ["Governance", "Board committees oversee ESG", "Embedded oversight"],
                    ],
                    widths=[43 * mm, 52 * mm, 45 * mm],
                ),
                Spacer(1, 2 * mm),
                p(
                    "<b>Materiality:</b> cocoa traceability, farmer income and child-labor remediation affect "
                    "supply continuity, reputation and cost. Packaging regulation and Scope 3 emissions can "
                    "change capex and product economics."
                ),
            ],
            [
                section("FREQUENCY ANALYSIS TEMPLATE"),
                line_chart(
                    [100, 103, 98, 106, 110, 105, 114, 108, 116, 111, 120, 117, 123],
                    ["M1", "", "M3", "", "M5", "", "M7", "", "M9", "", "M11", "", "M13"],
                    width=390,
                    height=112,
                    color=BLUE,
                    title_text="LOW-FREQUENCY PRICE INDEX // ILLUSTRATIVE",
                ),
                Spacer(1, 2 * mm),
                terminal_table(
                    [
                        ["FREQUENCY", "TEST", "INTERPRETATION"],
                        ["Daily", "Return / volume z-score", "Event response"],
                        ["Weekly", "Momentum + beta", "Trading regime"],
                        ["Monthly", "Total return / drawdown", "Investment outcome"],
                        ["Quarterly", "Price vs earnings revision", "Fundamental link"],
                    ],
                    widths=[40 * mm, 61 * mm, 50 * mm],
                ),
                Spacer(1, 2 * mm),
                p(
                    "Licensed Bloomberg PX_LAST, PX_VOLUME and adjusted-price exports are required to "
                    "populate this template. No invented terminal observations are represented as actual."
                ),
            ],
        )
    )
    story.append(source_note("Mondelēz Reporting & Disclosure portal and 2025 10-K. Price visual is illustrative."))
    story.append(PageBreak())

    # Q3
    story += title(
        "Q3 // FIVE-ASSET EQUITY PORTFOLIO // PAGE 1 OF 3",
        "Food & agro basket construction",
        "BRITANNIA · NESTLÉ INDIA · TATA CONSUMER · VARUN BEVERAGES · GODREJ AGROVET",
    )
    assets = [
        ["ASSET", "ROLE", "EQ. WT", "VOL. PROXY", "RISK-PARITY WT"],
        ["Britannia", "Packaged food quality", "20.0%", "19.8%", "20.8%"],
        ["Nestlé India", "Premium nutrition", "20.0%", "18.4%", "22.4%"],
        ["Tata Consumer", "Diversified staples", "20.0%", "21.6%", "19.1%"],
        ["Varun Beverages", "Growth / beverages", "20.0%", "28.8%", "14.3%"],
        ["Godrej Agrovet", "Upstream agro exposure", "20.0%", "24.1%", "17.1%"],
        ["Cash residual", "Rebalancing buffer", "0.0%", "0.0%", "6.3%"],
    ]
    story.append(terminal_table(assets, widths=[55 * mm, 85 * mm, 34 * mm, 42 * mm, 48 * mm]))
    story.append(Spacer(1, 3 * mm))
    story.append(
        two_col(
            [
                section("CONSTRUCTION LOGIC"),
                *bullet(
                    [
                        "Equal weight is transparent and avoids estimate error.",
                        "Volatility parity weights inversely to trailing volatility; no covariance optimization is assumed.",
                        "Monthly rebalancing limits drift while avoiding daily turnover.",
                        "NIFTY 50 Total Return Index is the benchmark.",
                        "Corporate-action-adjusted prices and INR total returns are required inputs.",
                    ]
                ),
            ],
            [
                section("RISK-PARITY WEIGHT CALCULATION"),
                p(
                    "Raw weight: <font color='#ff9f1c'>wᵢ = (1 / σᵢ) / Σ(1 / σⱼ)</font><br/>"
                    "A 6.3% cash buffer is included for execution and rounded weights. True equal-risk "
                    "contribution would additionally use the covariance matrix."
                ),
                Spacer(1, 2 * mm),
                bar_chart(
                    ["Britannia", "Nestlé", "Tata Cons.", "Varun Bev.", "Godrej Agro.", "Cash"],
                    [20.8, 22.4, 19.1, 14.3, 17.1, 6.3],
                    width=380,
                    height=110,
                    suffix="%",
                ),
            ],
        )
    )
    story.append(source_note("Weights and volatility inputs are a classroom analytical sample pending Bloomberg return exports."))
    story.append(PageBreak())

    story += title(
        "Q3 // FIVE-ASSET EQUITY PORTFOLIO // PAGE 2 OF 3",
        "Performance & drawdown",
        "Demonstration analytics  |  Annualized  |  Risk-free assumption: 6.5%",
    )
    perf = [
        ["PORTFOLIO", "ANN. RETURN", "VOLATILITY", "SHARPE", "MAX DRAWDOWN", "1Y ROLLING VOL"],
        ["Equal weight", "17.4%", "16.1%", "0.68x", "-17.8%", "14.2–22.6%"],
        ["Volatility parity", "16.2%", "13.8%", "0.70x", "-14.9%", "12.4–19.1%"],
        ["NIFTY 50 TRI", "13.5%", "14.6%", "0.48x", "-16.3%", "12.8–20.5%"],
    ]
    story.append(terminal_table(perf, widths=[57 * mm, 42 * mm, 42 * mm, 37 * mm, 48 * mm, 48 * mm]))
    story.append(Spacer(1, 3 * mm))
    story.append(
        two_col(
            [
                line_chart(
                    [100, 104, 99, 109, 116, 112, 123, 119, 134, 141, 137, 153, 161],
                    ["Y0", "", "", "Y1", "", "", "Y2", "", "", "Y3", "", "", "Y4"],
                    width=390,
                    height=135,
                    color=ORANGE,
                    title_text="EQUAL WEIGHT // CUMULATIVE INDEX",
                ),
                p(
                    "Equal weight captures more upside from high-beta growth holdings but experiences "
                    "the larger drawdown."
                ),
            ],
            [
                line_chart(
                    [100, 103, 100, 107, 113, 111, 119, 117, 128, 133, 131, 143, 151],
                    ["Y0", "", "", "Y1", "", "", "Y2", "", "", "Y3", "", "", "Y4"],
                    width=390,
                    height=135,
                    color=GREEN,
                    title_text="VOLATILITY PARITY // CUMULATIVE INDEX",
                ),
                p(
                    "Volatility parity improves drawdown and volatility at the expense of some absolute "
                    "return; its marginally higher Sharpe indicates better risk efficiency."
                ),
            ],
        )
    )
    story.append(
        source_note(
            "All performance statistics on this page are explicitly modeled demonstration results. "
            "Recompute with Bloomberg daily total returns before submission as empirical evidence."
        )
    )
    story.append(PageBreak())

    story += title(
        "Q3 // FIVE-ASSET EQUITY PORTFOLIO // PAGE 3 OF 3",
        "Factor attribution vs NIFTY 50 TRI",
        "Market · size · value proxies  |  Active-return decomposition",
    )
    factor = [
        ["SOURCE", "EQUAL WT CONTRIBUTION", "RISK PARITY CONTRIBUTION", "INTERPRETATION"],
        ["Market beta", "+1.4%", "+1.1%", "Bull-market participation"],
        ["Size tilt", "+0.8%", "+0.3%", "Mid-cap growth exposure"],
        ["Value tilt", "-0.6%", "-0.3%", "Quality portfolio is expensive"],
        ["Sector / quality", "+1.7%", "+1.4%", "Brand and distribution alpha"],
        ["Selection residual", "+0.6%", "+0.2%", "Stock-specific outcome"],
        ["Total active return", "+3.9%", "+2.7%", "Vs NIFTY 50 TRI"],
    ]
    story.append(terminal_table(factor, widths=[55 * mm, 55 * mm, 62 * mm, 92 * mm]))
    story.append(Spacer(1, 3 * mm))
    story.append(
        two_col(
            [
                bar_chart(
                    ["Market", "Size", "Value", "Quality", "Selection"],
                    [1.4, 0.8, -0.6, 1.7, 0.6],
                    width=390,
                    height=125,
                    suffix="%",
                ),
                p(
                    "Equal weight's excess return is primarily compensation for quality/sector concentration "
                    "plus a positive size tilt—not pure manager skill."
                ),
            ],
            [
                section("IMPLEMENTATION / CONTROLS"),
                *bullet(
                    [
                        "Use Bloomberg TOT_RETURN_INDEX_GROSS_DVDS or adjusted daily closes.",
                        "Align calendars; forward-fill only benchmark holidays, never missing asset prices.",
                        "Winsorize data errors, not genuine market moves.",
                        "Estimate rolling 252-day volatility and 36-month factor betas.",
                        "Report transaction costs and turnover separately.",
                        "Stress cocoa, sugar, monsoon and INR depreciation together.",
                    ]
                ),
            ],
        )
    )
    story.append(source_note("Attribution is a modeled example using broad factor-proxy logic, not a licensed Bloomberg regression output."))
    story.append(PageBreak())

    # Q4
    story += title(
        "Q4 // COMMODITY & FX // PAGE 1 OF 3",
        "Cocoa × USD/INR dashboard",
        "Food-sector cost transmission: imported commodity inflation translated into rupees",
    )
    story.append(
        metric_strip(
            [
                ("COCOA 12M", "+18.4%", "red"),
                ("USD/INR 12M", "+2.7%", "red"),
                ("INR COCOA", "+21.6%", "red"),
                ("RETURN CORR.", "+0.18", "white"),
                ("LEAD / LAG", "FX → COCOA +2D", "orange"),
            ]
        )
    )
    story.append(Spacer(1, 3 * mm))
    commodity = [
        ["COMMODITY", "USE", "5Y VOL", "PRIMARY DRIVER", "FOOD-SECTOR LINK"],
        ["Cocoa", "Chocolate", "High", "West Africa supply", "Direct"],
        ["Palm oil", "Fats / bakery", "High", "Indonesia/Malaysia", "Direct"],
        ["Wheat", "Biscuits / flour", "Medium", "Crop / policy", "Direct"],
        ["Sugar", "Sweeteners", "Medium", "India/Brazil crop", "Direct"],
        ["Brent", "Freight / packaging", "Medium", "OPEC / geopolitics", "Indirect"],
    ]
    fx = [
        ["PAIR", "ROLE", "KEY DRIVER"],
        ["USD/INR", "Import translation", "Oil, flows, RBI"],
        ["EUR/USD", "Global dollar", "Rates / growth"],
        ["USD/BRL", "Sugar origin", "Brazil terms of trade"],
        ["USD/MYR", "Palm origin", "Malaysia exports"],
        ["GBP/USD", "Risk / rates", "BoE / Fed"],
    ]
    story.append(two_col([section("COMMODITY MONITOR"), terminal_table(commodity, widths=[31 * mm, 34 * mm, 27 * mm, 46 * mm, 42 * mm])], [section("FX MONITOR"), terminal_table(fx, widths=[38 * mm, 48 * mm, 61 * mm])], (0.56, 0.44)))
    story.append(Spacer(1, 3 * mm))
    story.append(
        p(
            "<b>Core insight.</b> For an Indian food manufacturer, USD cocoa can rise even when the rupee "
            "strengthens; when both cocoa and USD/INR rise, local-currency cost inflation compounds. "
            "Procurement hedges must therefore consider commodity and FX jointly, not as isolated books.",
            "Callout",
        )
    )
    story.append(source_note("Dashboard values are a clearly labeled classroom sample; replace with Bloomberg C 1 Comdty and USDINR Curncy exports."))
    story.append(PageBreak())

    story += title(
        "Q4 // COMMODITY & FX // PAGE 2 OF 3",
        "Ten-year event map",
        "Normalized indices  |  Cocoa USD vs cocoa INR vs USD/INR",
    )
    story.append(
        line_chart(
            [100, 92, 85, 90, 98, 109, 101, 122, 155, 138, 174, 206, 288, 244, 271],
            ["16", "", "17", "", "18", "", "19", "", "20", "", "22", "", "24", "", "26"],
            width=780,
            height=150,
            color=ORANGE,
            title_text="COCOA IN INR // NORMALIZED EVENT PATH (ILLUSTRATIVE)",
        )
    )
    story.append(Spacer(1, 3 * mm))
    events = [
        ["PERIOD", "EVENT", "EXPECTED CHANNEL"],
        ["2016–17", "Cocoa surplus / price decline", "Input-cost relief"],
        ["2020", "COVID demand + logistics shock", "Volatility; channel shift"],
        ["2022", "Russia–Ukraine / broad food inflation", "Freight, energy and currency"],
        ["2023–24", "West Africa crop failures", "Historic cocoa squeeze"],
        ["2024–25", "Inventory scarcity / price pass-through", "Volume elasticity"],
        ["2025–26", "Normalization vs structural climate risk", "Hedging and reformulation"],
    ]
    story.append(terminal_table(events, widths=[40 * mm, 105 * mm, 120 * mm]))
    story.append(Spacer(1, 2 * mm))
    story.append(
        p(
            "<b>News annotation rule:</b> include only events known before each return observation. "
            "Avoid explaining a ten-year chart with hindsight-only narratives; mark harvest reports, export "
            "data, central-bank events and company pricing announcements at their actual dates."
        )
    )
    story.append(source_note("Event chronology is public-history based; plotted path is illustrative rather than a Bloomberg extraction."))
    story.append(PageBreak())

    story += title(
        "Q4 // COMMODITY & FX // PAGE 3 OF 3",
        "Correlation, lead/lag & prediction",
        "Returns—not levels—to reduce spurious regression risk",
    )
    regression = [
        ["TEST", "SPECIFICATION", "DEMO RESULT", "READ"],
        ["Contemporaneous", "corr(r cocoa, r FX)", "+0.18", "Weak positive"],
        ["Lead/lag", "corr(r cocoaₜ, r FXₜ₊₂)", "+0.11", "Limited persistence"],
        ["FX predicts cocoa", "r cocoaₜ = α + βr FXₜ₋₁", "β 0.21; p 0.08", "Not 5% significant"],
        ["Cocoa predicts FX", "r FXₜ = α + βr cocoaₜ₋₁", "β 0.04; p 0.03", "Small effect"],
        ["INR adjustment", "(1+r cocoa)(1+r FX)-1", "+21.6% 12M", "Compounding matters"],
    ]
    story.append(terminal_table(regression, widths=[45 * mm, 95 * mm, 60 * mm, 65 * mm]))
    story.append(Spacer(1, 3 * mm))
    story.append(
        two_col(
            [
                section("MODEL"),
                p(
                    "<font color='#ff9f1c'>rFX,t = α + β₁ rCocoa,t−1 + β₂ rOil,t + β₃ ΔVIX,t + εt</font>"
                ),
                p(
                    "Use Newey–West standard errors; inspect residual autocorrelation and heteroskedasticity. "
                    "Out-of-sample accuracy matters more than in-sample significance."
                ),
            ],
            [
                section("ECONOMIC INTERPRETATION"),
                *bullet(
                    [
                        "Low correlation does not imply low procurement risk.",
                        "INR depreciation amplifies imported commodity inflation.",
                        "Statistical significance can coexist with immaterial economic magnitude.",
                        "Regimes matter: correlations rise during global supply shocks.",
                        "Hedge ratios should be re-estimated, not fixed permanently.",
                    ]
                ),
            ],
        )
    )
    story.append(
        source_note(
            "Regression numbers are demonstration outputs designed to show correct interpretation. "
            "Run the supplied specification on Bloomberg daily returns for the final empirical version."
        )
    )
    story.append(PageBreak())

    # Q5
    story += title(
        "Q5 // MUTUAL FUND FLOWS // PAGE 1 OF 2",
        "Equity and debt fund monitor",
        "Five funds per asset class  |  Three-year analytical template",
    )
    fund_data = [
        ["FUND", "CLASS", "3Y CAGR", "ROLL 12M", "3Y NET FLOW ₹CR", "FLOW/PERF CORR."],
        ["HDFC Flexi Cap", "Equity", "20.1%", "18.6%", "+18,420", "+0.42"],
        ["Parag Parikh Flexi Cap", "Equity", "19.4%", "17.9%", "+24,870", "+0.51"],
        ["SBI Bluechip", "Equity", "13.8%", "13.4%", "+4,920", "+0.18"],
        ["ICICI Pru Value Discovery", "Equity", "21.7%", "20.2%", "+9,180", "+0.37"],
        ["Nippon India Small Cap", "Equity", "25.6%", "22.5%", "+16,340", "+0.58"],
        ["ICICI Pru Corp Bond", "Debt", "7.5%", "8.1%", "+3,240", "+0.12"],
        ["HDFC Short Term Debt", "Debt", "7.2%", "7.6%", "+2,180", "+0.09"],
        ["SBI Magnum Gilt", "Debt", "6.8%", "7.9%", "-620", "-0.08"],
        ["Aditya Birla Sun Life Corp Bond", "Debt", "7.3%", "7.8%", "+1,460", "+0.15"],
        ["Kotak Bond Short Term", "Debt", "7.1%", "7.5%", "+980", "+0.06"],
    ]
    story.append(terminal_table(fund_data, widths=[75 * mm, 32 * mm, 34 * mm, 37 * mm, 55 * mm, 43 * mm], font_size=6))
    story.append(Spacer(1, 3 * mm))
    story.append(
        two_col(
            [
                section("FLOW / PERFORMANCE TEST"),
                p(
                    "For each fund, compute monthly net flow as a percentage of beginning AUM. Regress "
                    "current flow on lagged 3-, 6- and 12-month excess returns. Use category fixed effects "
                    "and robust standard errors."
                ),
            ],
            [
                section("CATEGORY BENCHMARKS"),
                terminal_table(
                    [
                        ["CATEGORY", "BENCHMARK"],
                        ["Flexi / large cap", "NIFTY 500 TRI"],
                        ["Value", "NIFTY 500 Value 50 TRI"],
                        ["Small cap", "NIFTY Smallcap 250 TRI"],
                        ["Corporate bond", "CRISIL Corp Bond Index"],
                        ["Short / gilt", "CRISIL duration-matched index"],
                    ],
                    widths=[65 * mm, 81 * mm],
                ),
            ],
        )
    )
    story.append(source_note("Fund metrics are illustrative placeholders. Replace all NAV, AUM and monthly-flow fields with ACE MF exports."))
    story.append(PageBreak())

    story += title(
        "Q5 // MUTUAL FUND FLOWS // PAGE 2 OF 2",
        "Persistence or mean reversion?",
        "Interpretation framework and quality controls",
    )
    story.append(
        two_col(
            [
                bar_chart(
                    ["PPFAS Flexi", "Nippon Small", "HDFC Flexi", "ICICI Value", "SBI Bluechip", "Debt avg."],
                    [0.51, 0.58, 0.42, 0.37, 0.18, 0.07],
                    width=390,
                    height=130,
                    suffix="",
                ),
                p(
                    "<b>Modeled read:</b> equity flows chase recent performance more strongly than debt "
                    "flows. Small-cap flow sensitivity is highest, consistent with retail pro-cyclicality."
                ),
            ],
            [
                section("PERSISTENCE TEST"),
                terminal_table(
                    [
                        ["HORIZON", "HYPOTHESIS", "READ"],
                        ["1–3 months", "Flow chasing", "Positive"],
                        ["6–12 months", "Performance persistence", "Mixed"],
                        ["12–24 months", "Mean reversion", "Stronger in equity"],
                        ["Debt", "Rate-cycle / liquidity", "Low return sensitivity"],
                    ],
                    widths=[37 * mm, 59 * mm, 50 * mm],
                ),
                Spacer(1, 3 * mm),
                section("DATA HYGIENE"),
                *bullet(
                    [
                        "Use direct plans consistently; do not mix regular plans.",
                        "Adjust for mergers, IDCW distributions and scheme reclassification.",
                        "Separate market-driven AUM changes from investor net flows.",
                        "Use category-appropriate total-return benchmarks.",
                        "Flag survivorship bias from closed or merged schemes.",
                    ]
                ),
            ],
        )
    )
    story.append(
        p(
            "<b>Conclusion.</b> Positive flow/performance correlation does not prove skill: investors may "
            "buy after returns have already occurred. Persistence should be tested on future excess returns, "
            "while controlling for style and category. A finding of subsequent underperformance would support "
            "return-chasing followed by mean reversion.",
            "Callout",
        )
    )
    story.append(source_note("Interpretation is methodological; empirical values require ACE MF monthly flow and NAV data."))
    story.append(PageBreak())

    # Methodology / references
    story += title(
        "APPENDIX // DATA GOVERNANCE",
        "Methods, sources & submission controls",
        "What is verified, what is modeled, and what must be refreshed",
    )
    story.append(
        two_col(
            [
                section("PUBLIC SOURCES USED"),
                terminal_table(
                    [
                        ["SOURCE", "USE"],
                        ["Britannia FY25 Annual Report", "Financials, dividend, contingencies, RPT"],
                        ["NSE corporate filings", "Annual report and shareholding"],
                        ["MoFPI Annual Report 2024–25", "Industry structure and growth"],
                        ["PIB food-processing releases", "GVA, exports, policy / PLI"],
                        ["Mondelēz FY25 10-K / release", "Peer financials and governance"],
                        ["Mondelēz ESG disclosure portal", "ESG progress / boundaries"],
                    ],
                    widths=[67 * mm, 76 * mm],
                ),
                Spacer(1, 3 * mm),
                section("PRIMARY LINKS"),
                p(
                    "Britannia: https://media.britannia.co.in/2_annual_report_25_V1_Digital_FIN_Hires_1_SAP_b1a1c4c085.pdf<br/>"
                    "MoFPI: https://www.mofpi.gov.in/<br/>"
                    "PIB: https://www.pib.gov.in/<br/>"
                    "Mondelēz 10-K: https://www.sec.gov/Archives/edgar/data/1103982/<br/>"
                    "Mondelēz ESG: https://www.mondelezinternational.com/Snacking-Made-Right/Reporting-and-Disclosure/"
                ),
            ],
            [
                section("LICENSED DATA REFRESH CHECKLIST"),
                terminal_table(
                    [
                        ["DATABASE", "FIELDS TO EXPORT"],
                        ["ProwessDX", "10Y P&L, BS, CF; borrowings; RPT; contingencies"],
                        ["Bloomberg", "Adjusted/unadjusted prices, volumes, actions, benchmarks"],
                        ["Bloomberg", "Cocoa, USD/INR, factor proxies, peer ESG"],
                        ["ACE MF", "Daily NAV, month-end AUM, monthly net flows"],
                    ],
                    widths=[42 * mm, 104 * mm],
                ),
                Spacer(1, 3 * mm),
                section("QUALITY CONTROLS"),
                *bullet(
                    [
                        "Never label modeled data as Bloomberg/ProwessDX/ACE MF output.",
                        "Preserve extraction date, ticker, field name and currency.",
                        "Reconcile annual totals to audited statements.",
                        "Use adjusted prices for returns; unadjusted prices for action analysis.",
                        "State annualization, risk-free rate and missing-data rules.",
                        "Retain spreadsheet formulas and raw export tabs for audit.",
                    ]
                ),
                Spacer(1, 3 * mm),
                p(
                    "<b>Disclosure.</b> This PDF is a polished academic draft. Verified public facts are "
                    "cited. Every licensed-database result that could not be accessed is explicitly labeled "
                    "illustrative or modeled, preventing fabricated provenance."
                ),
            ],
        )
    )
    return story


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(OUT),
        pagesize=PAGE,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=18 * mm,
        bottomMargin=13 * mm,
        title="Finance Data Lab — Food & Agro Products",
        author="Student Research Submission",
        subject="Britannia Industries, Mondelez, Portfolio, Cocoa-FX and Mutual Funds",
    )
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="normal",
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    doc.addPageTemplates([PageTemplate(id="terminal", frames=frame, onPage=page_background)])
    doc.build(build_story())
    print(OUT)


if __name__ == "__main__":
    main()
