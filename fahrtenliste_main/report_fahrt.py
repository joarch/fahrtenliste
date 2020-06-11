import collections
from collections import defaultdict
from datetime import datetime

from fahrtenliste_main.models import Fahrt


def get_report_data(von, bis, kilometerpauschale_faktor, name):
    report_beschreibung = "Fahrten im Zeitraum: {} bis {}".format(von.strftime("%d.%m.%Y"), bis.strftime("%d.%m.%Y"))
    fahrten_alle = Fahrt.objects.filter(datum__gte=von, datum__lte=bis)
    kunden = set()
    adressen = set()
    summe_entfernung = 0

    eindeutige_fahrten = defaultdict(list)
    for idx, fahrt in enumerate(fahrten_alle):
        kunden.add(fahrt.kunde or str(-1 * idx))
        key = "{}:{}:{}".format(fahrt.datum.strftime("%Y-%m-%d"),
                                fahrt.adresse.str_kurz() if fahrt.adresse else str(-1 * idx),
                                fahrt.entfernung)
        fahrt_daten = {
            "datum": fahrt.datum.strftime("%d.%m.%Y"),
            "adresse": fahrt.adresse.str_kurz() if fahrt.adresse else "",
            "entfernung": fahrt.entfernung,
            "kunde": fahrt.kunde.str_kurz_mit_anrede() if fahrt.kunde else "?",
            "adresse_id": fahrt.adresse.id if fahrt.adresse else -1 * idx,
        }
        eindeutige_fahrten[key].append(fahrt_daten)

    eindeutige_fahrten = collections.OrderedDict(sorted(eindeutige_fahrten.items()))
    for key, fahrten_endeutig in eindeutige_fahrten.items():
        # nur eindeutige Adressen und Kilometer zählen
        entfernung = fahrten_endeutig[0]["entfernung"] or 0
        adressen.add(fahrten_endeutig[0]["adresse_id"])
        summe_entfernung += entfernung

        # Datum, Adresse und Entfernung sollen nur in der ersten Zeile einer Adresse sichtbar sein
        for idx, fahrt in enumerate(fahrten_endeutig):
            if fahrt["entfernung"] is None:
                fahrt["entfernung"] = "?"
            if idx != 0:
                fahrt["datum"] = ""
                fahrt["adresse"] = ""
                fahrt["entfernung"] = ""

    kilometerpauschale = kilometerpauschale_faktor * summe_entfernung

    return {
        "name": name,
        "report_beschreibung": report_beschreibung,
        "eindeutige_fahrten": eindeutige_fahrten,
        "summe_entfernung": summe_entfernung,
        "anzahl_fahrten": len(fahrten_alle),
        "anzahl_kunden": len(kunden),
        "anzahl_adressen": len(adressen),
        "kilometerpauschale_faktor": kilometerpauschale_faktor,
        "kilometerpauschale": kilometerpauschale,
        "report_erstellt": datetime.today()
    }
