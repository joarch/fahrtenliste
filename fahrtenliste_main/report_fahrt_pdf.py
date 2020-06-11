import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 10)
        self.drawRightString(200 * mm, 10 * mm,
                             "Seite %d von %d" % (self._pageNumber, page_count))


def pdf_report(dir, report_data):
    filename = os.path.join(dir, "Entfernungspauschale.pdf")

    zeilen = [
        ['Datum', 'Adresse', 'Kunde', 'Entfernung\n(km)'],
    ]
    for fahrten in report_data["eindeutige_fahrten"].values():
        for fahrt in fahrten:
            # Fahrten am Tag
            adresse = fahrt["adresse"]
            adresse = adresse.replace(", ", "\n")
            zeilen.append([fahrt["datum"], adresse, fahrt["kunde"], fahrt["entfernung"]])

    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=15 * mm, bottomMargin=15 * mm,
                            title="Entfernungspauschale")
    story = list()
    story.append(Paragraph('Fahrtenliste', styles['Heading1']))
    story.append(Paragraph(report_data["name"] or "", styles['Heading2']))
    story.append(Paragraph(report_data["report_beschreibung"], styles['Heading3']))
    t = Table(zeilen, colWidths=[80, 200, 100, 60], repeatRows=(0,))
    t.hAlign = 'LEFT'
    t.spaceBefore = 10
    t.spaceAfter = 10
    t.setStyle(TableStyle(
        [('BOX', (0, 0), (-1, -1), 0.5, colors.black),
         ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
         ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black)]))
    story.append(t)
    story.append(Paragraph('&nbsp;', styles['Normal']))
    story.append(Paragraph(f'Insgesamt gefahrene Strecke: {report_data["summe_entfernung"]} km.', styles['Normal']))
    story.append(Paragraph('&nbsp;', styles['Normal']))
    kilometerpauschale_faktor = _format_decimal(report_data["kilometerpauschale_faktor"])
    kilometerpauschale = _format_decimal(report_data["kilometerpauschale"])
    story.append(Paragraph(
        f'Entfernungspauschale: {report_data["summe_entfernung"]} km'
        f' * {kilometerpauschale_faktor} EUR/km'
        f' = <b>{kilometerpauschale} EUR</b>',
        styles['Normal']))

    title = "Fahrtenliste: 01.05.2020 - 31.05.2020"

    def _onLaterPages(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawString(10 * mm, 10 * mm, title)
        canvas.restoreState()

    doc.build(story, canvasmaker=NumberedCanvas, onLaterPages=_onLaterPages)

    return filename


if __name__ == "__main__":
    pdf_report("...", None)


def _format_decimal(value):
    if value is None:
        return 0
    return "{0:,.2f}".format(value).replace(',', ' ').replace('.', ',')
