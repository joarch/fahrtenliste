import collections
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from fahrtenliste_main.models import Fahrt


def get_report_data(von, bis):
    report_beschreibung = "Fahrten im Zeitraum: {} bis {}".format(von.strftime("%d.%m.%Y"), bis.strftime("%d.%m.%Y"))
    fahrten_alle = Fahrt.objects.filter(datum__gte=von, datum__lte=bis)
    kunden = set()
    adressen = set()
    summe_entfernung = 0

    eindeutige_fahrten = defaultdict(list)
    for fahrt in fahrten_alle:
        kunden.add(fahrt.kunde)
        key = "{}:{}:{}".format(fahrt.datum.strftime("%Y-%m-%d"), fahrt.adresse.str_kurz(), fahrt.entfernung)
        fahrt_daten = {
            "datum": fahrt.datum.strftime("%d.%m.%Y"),
            "adresse": fahrt.adresse.str_kurz(),
            "entfernung": fahrt.entfernung,
            "kunde": fahrt.kunde.str_kurz(),
            "adresse_id": fahrt.adresse.id,
        }
        eindeutige_fahrten[key].append(fahrt_daten)

    eindeutige_fahrten = collections.OrderedDict(sorted(eindeutige_fahrten.items()))
    for key, fahrten_endeutig in eindeutige_fahrten.items():
        # nur eindeutige Adressen und Kilometer zählen
        adressen.add(fahrten_endeutig[0]["adresse_id"])
        summe_entfernung += fahrten_endeutig[0]["entfernung"]

        # Datum, Adresse und Entfernung sollen nur in der ersten Zeile einer Adresse sichtbar sein
        for idx, fahrt in enumerate(fahrten_endeutig):
            if idx != 0:
                fahrt["datum"] = ""
                fahrt["adresse"] = ""
                fahrt["entfernung"] = ""

    faktor = Decimal("0.3")
    entfernungspauschale = faktor * summe_entfernung

    return {
        "report_beschreibung": report_beschreibung,
        "eindeutige_fahrten": eindeutige_fahrten,
        "summe_entfernung": summe_entfernung,
        "anzahl_fahrten": len(fahrten_alle),
        "anzahl_kunden": len(kunden),
        "anzahl_adressen": len(adressen),
        "faktor" : faktor,
        "entfernungspauschale": entfernungspauschale,
        "report_erstellt": datetime.today()
    }
