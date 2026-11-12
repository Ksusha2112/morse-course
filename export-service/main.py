import csv
import io
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

app = FastAPI(title="Export Service")


class ExportRequest(BaseModel):
    original: str = Field(..., description="Исходный текст")
    morse: str = Field(..., description="Текст в азбуке Морзе")


FONT_NAME = "DejaVu"
BUNDLED_FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "DejaVuSans.ttf")
FONT_CANDIDATES = [
    BUNDLED_FONT,
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
]


def _register_font() -> str:
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(FONT_NAME, path))
            return FONT_NAME
    return "Helvetica"


FONT = _register_font()


def _wrap(text: str, width: int) -> list:
    lines = []
    for paragraph in text.splitlines() or [""]:
        while len(paragraph) > width:
            lines.append(paragraph[:width])
            paragraph = paragraph[width:]
        lines.append(paragraph)
    return lines


def _build_txt(data: ExportRequest) -> bytes:
    content = f"Исходный текст:\n{data.original}\n\nАзбука Морзе:\n{data.morse}\n"
    return content.encode("utf-8")


def _build_csv(data: ExportRequest) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";")
    writer.writerow(["Поле", "Значение"])
    writer.writerow(["Исходный текст", data.original])
    writer.writerow(["Азбука Морзе", data.morse])
    return buf.getvalue().encode("utf-8-sig")


def _build_pdf(data: ExportRequest) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 30 * mm

    c.setFont(FONT, 16)
    c.drawString(20 * mm, y, "Азбука Морзе — результат")
    y -= 15 * mm

    c.setFont(FONT, 12)
    c.drawString(20 * mm, y, "Исходный текст:")
    y -= 7 * mm
    for line in _wrap(data.original, 80):
        c.setFont(FONT, 11)
        c.drawString(20 * mm, y, line)
        y -= 6 * mm

    y -= 5 * mm
    c.setFont(FONT, 12)
    c.drawString(20 * mm, y, "Азбука Морзе:")
    y -= 7 * mm
    for line in _wrap(data.morse, 60):
        c.setFont(FONT, 11)
        c.drawString(20 * mm, y, line)
        y -= 6 * mm
        if y < 20 * mm:
            c.showPage()
            y = height - 20 * mm

    c.save()
    return buf.getvalue()


BUILDERS = {
    "txt": ("morse_result.txt", "text/plain; charset=utf-8", _build_txt),
    "csv": ("morse_result.csv", "text/csv; charset=utf-8", _build_csv),
    "pdf": ("morse_result.pdf", "application/pdf", _build_pdf),
}


@app.get("/health")
def health():
    return {"status": "ok", "service": "export"}


@app.post("/api/export/{fmt}")
def export(fmt: str, data: ExportRequest):
    if fmt not in BUILDERS:
        raise HTTPException(status_code=404, detail="Неизвестный формат")
    filename, media_type, builder = BUILDERS[fmt]
    content = builder(data)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
