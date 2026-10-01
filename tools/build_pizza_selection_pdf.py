from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Flowable, Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dossier" / "festin-napoles-seleccion-pizzas.pdf"

PAGE_W, PAGE_H = A4
MARGIN = 1.4 * cm

CREAM = colors.HexColor("#f3ebdd")
CREAM_SOFT = colors.HexColor("#d7cabb")
MUTED = colors.HexColor("#a89b8d")
RED = colors.HexColor("#b32025")
BLUE = colors.HexColor("#0b2a5b")
BLACK = colors.HexColor("#070707")
GRAPHITE = colors.HexColor("#101011")
LINE = colors.HexColor("#2a2a2a")


TRADIZIONALE = [
    ("Margherita", "Pomodoro, mozzarella fior di latte, albahaca fresca y aceite de oliva.", "6qpETtMBbKpQRhLDr-300-x.webp"),
    ("Diavola", "Pomodoro, mozzarella, salame italiano picante, cebolla morada y aceitunas.", "bs2psYbFd7P6mrRZd-300-x.webp"),
    ("Pepperoni", "Pomodoro, mozzarella, pepperoni artesanal y oregano.", "GKmk8swxEdjQAN24G-300-x.webp"),
    ("Carnivora", "Pomodoro, mozzarella, jamon italiano, pepperoni y salame.", "wMq29m4H9XDJuxER4-300-x.webp"),
    ("Napoletana", "Pomodoro, mozzarella, tomate fresco, oregano y aceite de oliva.", "pizza-napoletana.webp"),
    ("Vegetariana / Ortolana", "Mozzarella, champinones, pimenton asado, cebolla morada y aceitunas.", "pizza-vegetariana-ortolana.webp"),
    ("Fugazza", "Mozzarella, mix de cebollas caramelizadas, oregano y aceite de oliva.", "5JWzWJhwtWNHoCPQu-300-x.webp"),
]

SIGNATURE = [
    ("Prosciutto", "Pomodoro, mozzarella, prosciutto italiano, rucula, pecorino y aceite de oliva.", "gAYRo6DS8YvMf5zak-x-300.webp"),
    ("Guanciale", "Pomodoro, mozzarella, guanciale italiano, cebolla morada caramelizada y pecorino.", "y4fWrweX4oHvnR2Hc-300-x.webp"),
    ("Fresca", "Pesto de albahaca, mozzarella, tomates secos, albahaca fresca y pecorino.", "JEvmhYLk959XEMwXM-x-300.webp"),
    ("Verde Napoli", "Mozzarella, palta, cebolla morada, mascarpone artesanal y semillas.", "dFfo74LFahS2ejH8y-x-300.webp"),
    ("Bianca Tartufo", "Mozzarella, quesos blancos, crema suave, aceite de trufa y oregano.", "tqXWQWqchcxbgJwoj-300-x.webp"),
]


STYLES = {
    "eyebrow": ParagraphStyle("eyebrow", fontName="Helvetica-Bold", fontSize=8.5, leading=10, textColor=RED, spaceAfter=8),
    "title": ParagraphStyle("title", fontName="Times-Roman", fontSize=42, leading=43, textColor=CREAM, spaceAfter=10),
    "h2": ParagraphStyle("h2", fontName="Times-Roman", fontSize=30, leading=32, textColor=CREAM, spaceAfter=7),
    "lead": ParagraphStyle("lead", fontName="Helvetica", fontSize=12, leading=18, textColor=CREAM_SOFT, spaceAfter=16),
    "small": ParagraphStyle("small", fontName="Helvetica", fontSize=9, leading=13, textColor=MUTED),
    "card_title": ParagraphStyle("card_title", fontName="Times-Bold", fontSize=13.5, leading=15, textColor=CREAM, spaceAfter=2),
    "card_text": ParagraphStyle("card_text", fontName="Helvetica", fontSize=7.3, leading=9.6, textColor=CREAM_SOFT),
}


class Rule(Flowable):
    def __init__(self, color=LINE, width=1):
        super().__init__()
        self.height = 0.35 * cm
        self.color = color
        self.rule_width = width

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.rule_width)
        self.canv.line(0, self.height / 2, PAGE_W - 2 * MARGIN, self.height / 2)


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BLACK)
    canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    canvas.setStrokeColor(colors.Color(1, 1, 1, alpha=0.08))
    canvas.rect(MARGIN, MARGIN, PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN, stroke=1, fill=0)
    canvas.setFillColor(colors.Color(0.07, 0.07, 0.075, alpha=0.8))
    canvas.circle(PAGE_W * 0.88, PAGE_H * 0.83, 8.5 * cm, stroke=0, fill=1)
    canvas.setFillColor(colors.Color(0.10, 0.02, 0.025, alpha=0.65))
    canvas.circle(PAGE_W * 0.12, PAGE_H * 0.28, 6.5 * cm, stroke=0, fill=1)
    canvas.setFont("Helvetica-Bold", 7)
    canvas.setFillColor(RED)
    canvas.drawString(MARGIN + 0.25 * cm, PAGE_H - MARGIN - 0.5 * cm, "FESTIN NAPOLES")
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN + 0.25 * cm, MARGIN - 0.55 * cm, "Seleccion de pizzas para eventos")
    canvas.drawRightString(PAGE_W - MARGIN - 0.25 * cm, MARGIN - 0.55 * cm, str(canvas.getPageNumber()))
    canvas.restoreState()


def pizza_card(item):
    name, description, image_name = item
    image_size = 3.75 * cm
    table = Table(
        [
            [Image(str(ROOT / image_name), width=image_size, height=image_size)],
            [Paragraph(name, STYLES["card_title"])],
            [Paragraph(description, STYLES["card_text"])],
        ],
        colWidths=[5.15 * cm],
        rowHeights=[image_size, None, None],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GRAPHITE),
                ("BOX", (0, 0), (-1, -1), 0.65, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return table


def pizza_grid(items, columns=3):
    rows = []
    for index in range(0, len(items), columns):
        row_items = items[index:index + columns]
        rows.append([pizza_card(item) for item in row_items] + [""] * (columns - len(row_items)))
    table = Table(rows, colWidths=[5.45 * cm] * columns, hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return table


def build_pdf():
    OUTPUT.parent.mkdir(exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=1.9 * cm,
        bottomMargin=1.7 * cm,
    )
    story = [
        Spacer(1, 2.7 * cm),
        Paragraph("SELECCION DE PIZZAS", STYLES["eyebrow"]),
        Paragraph("Festin Napoles", STYLES["title"]),
        Paragraph(
            "Menu editorial para clientes con reserva confirmada. Elige tus preferencias Tradizionale y Signature, o dejanos definir una seleccion equilibrada para tu evento.",
            STYLES["lead"],
        ),
        Rule(RED, 0.8),
        Spacer(1, 0.25 * cm),
        Paragraph(
            "Referencia de produccion: 1 pizza napolitana de 30 a 32 cm cada 2 personas. Para experiencias mixtas sugerimos combinar clasicas italianas con recetas de autor.",
            STYLES["small"],
        ),
        Spacer(1, 3.0 * cm),
        Paragraph("Como elegir", STYLES["h2"]),
        Paragraph(
            "Puedes responder el correo de confirmacion indicando tus favoritas. Si no tienes preferencias, Festin Napoles prepara una seleccion balanceada segun el tipo de evento y cantidad de invitados.",
            STYLES["lead"],
        ),
        PageBreak(),
        Paragraph("TRADIZIONALE", STYLES["eyebrow"]),
        Paragraph("Tradizionale", STYLES["h2"]),
        Paragraph("Pensadas para compartir, con sabores reconocibles y equilibrio napolitano.", STYLES["lead"]),
        pizza_grid(TRADIZIONALE),
        PageBreak(),
        Paragraph("SIGNATURE", STYLES["eyebrow"]),
        Paragraph("Signature", STYLES["h2"]),
        Paragraph("Combinaciones con mas caracter para elevar la experiencia del evento.", STYLES["lead"]),
        pizza_grid(SIGNATURE),
        Spacer(1, 0.7 * cm),
        Rule(BLUE, 0.8),
        Spacer(1, 0.25 * cm),
        Paragraph(
            "Para confirmar preferencias, responde el correo de reserva con los nombres de las pizzas elegidas. Tambien puedes pedir que el pizzaiolo defina una seleccion equilibrada para el evento.",
            STYLES["small"],
        ),
    ]
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT)
