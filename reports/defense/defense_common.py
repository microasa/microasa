"""Shared layout helpers for the dissertation-defence books (no paper content here)."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

F = "/usr/share/fonts/truetype/dejavu/"
for n, f in [("S", "DejaVuSerif.ttf"), ("SB", "DejaVuSerif-Bold.ttf"), ("SS", "DejaVuSans.ttf"),
             ("SSB", "DejaVuSans-Bold.ttf"), ("M", "DejaVuSansMono.ttf")]:
    pdfmetrics.registerFont(TTFont(n, F + f))
pdfmetrics.registerFontFamily("S", normal="S", bold="SB", italic="S", boldItalic="SB")
pdfmetrics.registerFontFamily("SS", normal="SS", bold="SSB", italic="SS", boldItalic="SSB")

INK, GRY, LINE, FILL = (colors.HexColor(c) for c in ("#191919", "#666666", "#c8ccd2", "#f2f4f7"))
ACC = colors.HexColor("#1d5fa8")
WARN = colors.HexColor("#b54708")
ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["Normal"], fontName="S", fontSize=10.2, leading=15, alignment=TA_JUSTIFY,
                      textColor=INK, spaceAfter=7)
ch = ParagraphStyle("ch", parent=body, fontName="SSB", fontSize=19, leading=24, spaceAfter=12, textColor=ACC,
                    alignment=0)
h2 = ParagraphStyle("h2", parent=body, fontName="SSB", fontSize=12.3, leading=16, spaceBefore=11, spaceAfter=5,
                    alignment=0, keepWithNext=1)
h3 = ParagraphStyle("h3", parent=body, fontName="SSB", fontSize=10.4, leading=14, spaceBefore=7, spaceAfter=3,
                    alignment=0, keepWithNext=1)
eq = ParagraphStyle("eq", parent=body, alignment=TA_CENTER, spaceBefore=3, spaceAfter=8, fontSize=10.3)
cap = ParagraphStyle("cap", parent=body, fontName="SS", fontSize=8.6, leading=11.5, textColor=GRY, spaceAfter=9)
cell = ParagraphStyle("cell", parent=body, fontName="SS", fontSize=8, leading=10.3, alignment=0, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="SSB")
bul = ParagraphStyle("bul", parent=body, leftIndent=14, bulletIndent=3, spaceAfter=4, alignment=0)
box = ParagraphStyle("box", parent=body, fontName="SS", fontSize=9.4, leading=13.6,
                     backColor=colors.HexColor("#eef4fb"), borderColor=ACC, borderWidth=0.8, borderPadding=8,
                     spaceBefore=6, spaceAfter=12, alignment=0)
warn = ParagraphStyle("warn", parent=box, backColor=colors.HexColor("#fdf3e7"), borderColor=WARN)
theory = ParagraphStyle("theory", parent=body, fontSize=9.9, leading=14.4, backColor=colors.HexColor("#f4f6f9"),
                        borderColor=colors.HexColor("#9aa3ad"), borderWidth=0.6, borderPadding=7, spaceBefore=5,
                        spaceAfter=10)
app = ParagraphStyle("app", parent=body, fontSize=9.9, leading=14.4, backColor=colors.HexColor("#eef7f1"),
                     borderColor=colors.HexColor("#067647"), borderWidth=0.6, borderPadding=7, spaceBefore=3,
                     spaceAfter=11)
q = ParagraphStyle("q", parent=body, fontName="SSB", fontSize=9.8, leading=13.5, spaceBefore=7, spaceAfter=2,
                   alignment=0, keepWithNext=1, textColor=ACC)
a = ParagraphStyle("a", parent=body, fontSize=9.8, leading=14, leftIndent=12, spaceAfter=4)
title = ParagraphStyle("t", parent=body, fontName="SSB", fontSize=26, leading=32, alignment=TA_CENTER, textColor=ACC)
subt = ParagraphStyle("st", parent=body, fontName="SS", fontSize=12.5, leading=17.5, alignment=TA_CENTER)
small = ParagraphStyle("sm", parent=body, fontName="SS", fontSize=9, alignment=TA_CENTER, textColor=GRY)


class Book:
    def __init__(self, footer_text):
        self.S = []
        self.footer_text = footer_text
        self.nq = 0

    def P(self, t, s=body):
        self.S.append(Paragraph(t, s))

    def B(self, items):
        for t in items:
            self.S.append(Paragraph(t, bul, bulletText="•"))

    def EQ(self, t):
        self.P(t, eq)

    def BOX(self, t):
        self.P(t, box)

    def WARN(self, t):
        self.P(t, warn)

    def T(self, head, text):
        """Theory block."""
        self.S.append(Paragraph(f"<b>Teori — {head}.</b> {text}", theory))

    def APP(self, text):
        """Application block: how the theory is used in the paper."""
        self.S.append(Paragraph(f"<b>Aplikasi di paper ini.</b> {text}", app))

    def CH(self, t, first=False):
        if not first:
            self.S.append(PageBreak())
        self.P(t, ch)

    def H2(self, t):
        self.P(t, h2)

    def H3(self, t):
        self.P(t, h3)

    def QA(self, question, answer, tip=None):
        self.nq += 1
        parts = [Paragraph(f"P{self.nq}. {question}", q), Paragraph(answer, a)]
        if tip:
            parts.append(Paragraph(f"<font color='#b54708'><b>Kunci:</b></font> {tip}", a))
        self.S.append(KeepTogether(parts))

    def TBL(self, rows, widths, caption):
        data = [[Paragraph(str(c), cellb if i == 0 else cell) for c in r] for i, r in enumerate(rows)]
        t = Table(data, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, LINE), ("BACKGROUND", (0, 0), (-1, 0), FILL),
                               ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 4),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]))
        self.S.append(KeepTogether([Paragraph(caption, cap), t, Spacer(1, 8)]))

    def cover(self, ttl, subtitle, lines):
        self.S += [Spacer(1, 4.5 * cm), Paragraph(ttl, title), Spacer(1, 0.6 * cm), Paragraph(subtitle, subt),
                   Spacer(1, 1.2 * cm)] + [Paragraph(x, small) for x in lines] + [PageBreak()]
        self.P("Daftar Isi", ch)
        toc = TableOfContents()
        toc.levelStyles = [ParagraphStyle("t0", fontName="SSB", fontSize=10.5, leading=15),
                           ParagraphStyle("t1", fontName="SS", fontSize=9, leading=12.5, leftIndent=16,
                                          textColor=GRY)]
        self.S.append(toc)

    def build(self, path, doc_title):
        footer_text = self.footer_text

        class Doc(SimpleDocTemplate):
            def afterFlowable(self, f):
                if isinstance(f, Paragraph) and f.style.name in ("ch", "h2") and f.getPlainText() != "Daftar Isi":
                    self.notify("TOCEntry", (0 if f.style.name == "ch" else 1, f.getPlainText(), self.page))

        def footer(canvas, doc):
            if doc.page == 1:
                return
            canvas.saveState()
            canvas.setFont("SS", 7.5)
            canvas.setFillColor(GRY)
            canvas.drawString(2.2 * cm, 1.2 * cm, footer_text)
            canvas.drawRightString(A4[0] - 2.2 * cm, 1.2 * cm, str(doc.page))
            canvas.restoreState()

        doc = Doc(path, pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=2 * cm,
                  bottomMargin=2 * cm, title=doc_title, author="")
        doc.multiBuild(self.S, onFirstPage=footer, onLaterPages=footer)
