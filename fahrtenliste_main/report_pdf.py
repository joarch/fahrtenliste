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


def pdf_report(name, zeitraum):
    my_data = [
        ['Datum', 'Adresse', 'Kunde', 'Entfernung\n(km)'],
    ]

    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate('test.pdf', pagesize=A4, topMargin=15 * mm, bottomMargin=15 * mm)
    story = list()
    story.append(Paragraph('Fahrtenliste', styles['Heading1']))
    story.append(Paragraph(name, styles['Heading2']))
    story.append(Paragraph('Zeitraum: 01.05.2020 bis 31.05.2020', styles['Heading3']))
    t = Table(my_data, colWidths=[80, 200, 100, 60], repeatRows=(0,))
    t.hAlign = 'LEFT'
    t.spaceBefore = 10
    t.spaceAfter = 10
    t.setStyle(TableStyle(
        [('BOX', (0, 0), (-1, -1), 0.5, colors.black),
         ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
         ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black)]))
    story.append(t)
    story.append(Paragraph('&nbsp;', styles['Normal']))
    story.append(Paragraph('Insgesamt gefahrene Strecke: 12 km.', styles['Normal']))
    story.append(Paragraph('&nbsp;', styles['Normal']))
    story.append(Paragraph('Entfernungspauschale: 12 km * 0,31 EUR/km = <b>3,72 EUR</b>', styles['Normal']))

    title = "Fahrtenliste: 01.05.2020 - 31.05.2020"

    def _onLaterPages(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawString(10 * mm, 10 * mm, title)
        canvas.restoreState()

    doc.build(story, canvasmaker=NumberedCanvas, onLaterPages=_onLaterPages)


if __name__ == "__main__":
    pdf_report("...", None)
