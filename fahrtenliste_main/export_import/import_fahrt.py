import datetime
import os

import reversion

from fahrtenliste_main.datum_util import str_datum
from fahrtenliste_main.export_import.excel import is_empty_value
from fahrtenliste_main.export_import.import_adresse import adresse_key
from fahrtenliste_main.export_import.import_adresse import neue_adresse
from fahrtenliste_main.export_import.import_kunde import kunde_key
from fahrtenliste_main.export_import.import_kunde import neuer_kunde
from fahrtenliste_main.export_import.imports import import_von_excel
from fahrtenliste_main.fahrt_util import get_next_fahrt_nr
from fahrtenliste_main.historisch import str_kunde_historisch, str_adresse_historisch
from fahrtenliste_main.historisch import to_kunde_historisch
from fahrtenliste_main.models import Adresse, Kunde
from fahrtenliste_main.models import Fahrt
from fahrtenliste_main.temp_dir import get_temp_file_path
from fahrtenliste_main.temp_dir import write_to_temp_file

IMPORT_FORMAT_FAHRT_STANDARD = {
    "id": "fahrtenliste",
    "typ": "Fahrt",
    "name": "Fahrtenliste Fahrt",
    "beschreibung": "Fahrtenliste Standard Format Fahrt",
    "filemuster": "Fahrtenliste_Fahrten_.*\\.xlsx",
    "start_row": 2,
    "nicht_im_import_aktion": "WARNUNG",
    "columns":
        {
            "A": "id",
            "B": "fahrt_nr",
            "C": "datum",
            "D": "anrede",
            "E": "vorname",
            "F": "nachname",
            "G": "strasse",
            "H": "plz",
            "I": "ort",
            "J": "entfernung",
            "K": "betrag",
            "L": "steuer",
            "M": "konto",
            "N": "kommentar"
        }
}

IMPORT_FORMATE_FAHRT = {
    IMPORT_FORMAT_FAHRT_STANDARD["id"]: IMPORT_FORMAT_FAHRT_STANDARD
}


def do_import_fahrten(user, file, format_key, dry_run=True, temp_file_name=None):
    import_format = IMPORT_FORMATE_FAHRT.get(format_key)
    if import_format is None:
        raise RuntimeError(f"Unbekanntes Import Format '{format_key}'!")

    file_name = file.name if file is not None else temp_file_name

    if dry_run:
        return _import_fahrt(user, file, import_format, dry_run, temp_file_name)
    else:
        with reversion.create_revision():
            reversion.set_user(user)
            reversion.set_comment("Import Fahrten ({}): {}".format(import_format["name"], file_name))
            return _import_fahrt(user, file, import_format, dry_run, temp_file_name=temp_file_name)


def _import_fahrt(user, file, import_format, dry_run, tempfile_mit_timestamp=False, temp_file_name=None):
    neu = list()
    geloescht = list()
    geaendert = list()
    unveraendert = list()
    warnung = list()
    fahrten_in_source = list()

    file_name = file.name if file is not None else temp_file_name

    if temp_file_name is None:
        temp_file_path = write_to_temp_file(user, file, tempfile_mit_timestamp)
        temp_file_name = os.path.basename(temp_file_path)
    else:
        if file is not None:
            raise RuntimeError("Fehler In-Memory-File und temp_file_name übergeben.")
        temp_file_path = get_temp_file_path(user, temp_file_name)

    fahrten_source = import_von_excel(temp_file_path, import_format)
    fahrten_source_ohne_id = list(filter(lambda f: is_empty_value(f["id"]), fahrten_source))
    fahrten_source_mit_id = list(filter(lambda f: not is_empty_value(f["id"]), fahrten_source))
    fahrten_source_by_id = {f["id"]: f for f in fahrten_source_mit_id}

    kunden_destination = Kunde.objects.filter()
    kunden_destination_by_key = {kunde_key(k.vorname, k.nachname): k for k in kunden_destination}

    adressen_destination = Adresse.objects.filter()
    adressen_destination_by_key = {adresse_key(a.strasse, a.plz, a.ort): a for a in adressen_destination}

    von, bis = _ermittel_zeitraum(fahrten_source)

    fahrten_destination = Fahrt.objects.filter(datum__gte=von, datum__lte=bis)
    fahrten_destination_by_id = {f.id: f for f in fahrten_destination}
    fahrten_destination_by_key = {
        fahrt_key(str_datum(f.datum), _kunde_aus_fahrt(f).vorname, _kunde_aus_fahrt(f).nachname): f for f
        in fahrten_destination}

    # alle Fahrten ohne Id Spalte (in der Regel neue Fahrten)
    for fahrt_source in fahrten_source_ohne_id:
        key = fahrt_key(str_datum(fahrt_source["datum"]), fahrt_source["vorname"], fahrt_source["nachname"])
        fahrt_destination = fahrten_destination_by_key.get(key)

        # Fallback Kunde mit eindeutigem Nachnamen
        if fahrt_destination is None:
            kunde = kunden_destination_by_key.get(kunde_key(fahrt_source["vorname"], fahrt_source["nachname"]))
            if kunde is None:
                kunde = _find_eindeutigen_kunden_mit_name(fahrt_source)
                if kunde is not None:
                    fahrt_source["vorname"] = kunde.vorname
                    fahrt_source["nachname"] = kunde.nachname
                    key = fahrt_key(str_datum(fahrt_source["datum"]), fahrt_source["vorname"], fahrt_source["nachname"])
                    fahrt_destination = fahrten_destination_by_key.get(key)

        _import_fahrt_kunde_adresse(fahrt_source, fahrt_destination, fahrten_in_source,
                                    kunden_destination_by_key, adressen_destination_by_key,
                                    neu, geaendert, unveraendert, warnung, dry_run)

    # alle Fahrten mit Id Spalte
    for id, fahrt_source in fahrten_source_by_id.items():
        # Suche mit Id
        fahrt_destination = fahrten_destination_by_id.get(id)
        _import_fahrt_kunde_adresse(fahrt_source, fahrt_destination, fahrten_in_source,
                                    kunden_destination_by_key, adressen_destination_by_key,
                                    neu, geaendert, unveraendert, warnung, dry_run)

    nicht_im_import_aktion = import_format["nicht_im_import_aktion"]
    if nicht_im_import_aktion == "WARNUNG":
        # Warnungen bei Fahrten, die nicht mehr in der Liste stehen
        # Hinweis: es werden keine Fahrten automatisch gelöscht
        for id, fahrt_destination in fahrten_destination_by_id.items():
            if fahrt_destination not in fahrten_in_source:
                warnung.append(f"fehlt im Import: {fahrt_mit_link(fahrt_destination)}")
    elif nicht_im_import_aktion == "NICHTS":
        pass
    else:
        raise RuntimeError(f"Unbekannte 'nicht_im_import_aktion': '{nicht_im_import_aktion}'")

    return {
        "format": "{}".format(import_format["name"]),
        "beschreibung": "{}.<span style='font-weight: bold;' >Import Zeitraum: {} bis {}.</span>".format(
            import_format["beschreibung"],
            von.strftime('%d.%m.%Y'),
            bis.strftime('%d.%m.%Y')),
        "filename": file_name,
        "temp_file_name": temp_file_name,
        "typ": import_format["typ"],
        "format_key": import_format["id"],
        "timestamp": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "neu": neu,
        "geloescht": geloescht,
        "geaendert": geaendert,
        "unveraendert": unveraendert,
        "warnung": warnung,
        "simulation": "ja" if dry_run else "nein",
    }


def _import_fahrt_kunde_adresse(fahrt_source, fahrt_destination, fahrten_in_source,
                                kunden_destination_by_key, adressen_destination_by_key,
                                neu, geaendert, unveraendert, warnungen, dry_run):
    key_kunde = kunde_key(fahrt_source["vorname"], fahrt_source["nachname"])
    key_adresse = adresse_key(fahrt_source["strasse"], fahrt_source["plz"], fahrt_source["ort"])

    # Fahrt
    if fahrt_destination is None:
        if is_empty_value(fahrt_source["fahrt_nr"]):
            fahrt_source["fahrt_nr"] = get_next_fahrt_nr()

        fahrt_destination = neue_fahrt(fahrt_source)
        new = True
        aenderungen = []
    else:
        if is_empty_value(fahrt_source["fahrt_nr"]):
            fahrt_source["fahrt_nr"] = fahrt_destination.fahrt_nr

        fahrten_in_source.append(fahrt_destination)
        new = False
        aenderungen = check_aenderung_fahrt(fahrt_source, fahrt_destination)

    # Adresse
    adresse_str = ""
    if key_adresse:
        adresse = adressen_destination_by_key.get(key_adresse)
        if adresse is None:
            # neue Adresse
            aenderungen.append("neue Adresse")
            adresse = neue_adresse(fahrt_source, [], dry_run)
            adressen_destination_by_key[key_adresse] = adresse
        if fahrt_destination.entfernung is None:
            # wenn keine Entfernung gegeben, dann Entfernung der Adresse übernehmen
            fahrt_destination.entfernung = adresse.entfernung
            aenderungen.append(f"Entfernung: neu='{adresse.entfernung}'")
        if fahrt_destination.adresse is None:
            fahrt_destination.adresse = adresse
            aenderungen.append("Adresse neu zugeordnet")
        elif adresse_key(fahrt_destination.adresse.strasse, fahrt_destination.adresse.plz,
                         fahrt_destination.adresse.ort) != key_adresse:
            aenderungen.append(f"Adresse: alt={fahrt_destination.adresse}")
            fahrt_destination.adresse = adresse

    # Kunde
    kunde_str = ""
    if key_kunde:
        kunde = kunden_destination_by_key.get(key_kunde)
        if kunde is None:
            # neuer Kunde
            aenderungen.append("neuer Kunde")
            kunde = neuer_kunde(fahrt_source, [], dry_run)
            kunden_destination_by_key[key_kunde] = kunde
            kunde.adresse = fahrt_destination.adresse
        if fahrt_destination.adresse is None and kunde.adresse is not None:
            # wenn Kunde ohne adresse im Input, dann Adresse des Kunden nehmen
            fahrt_destination.adresse = kunde.adresse
            aenderungen.append("Adresse aus dem Kunden neu übernommen")
            if fahrt_destination.entfernung is None:
                # wenn keine Entfernung gegeben, dann Entfernung der Adresse übernehmen
                fahrt_destination.entfernung = fahrt_destination.adresse.entfernung
                aenderungen.append(f"Entfernung: neu='{fahrt_destination.adresse.entfernung}'")
        if fahrt_destination.kunde is None:
            fahrt_destination.kunde = kunde
            aenderungen.append("Kunde neu zugeordnet")
        elif kunde_key(fahrt_destination.kunde.vorname, fahrt_destination.kunde.nachname) != key_kunde:
            aenderungen.append(f"Kunde: alt={fahrt_destination.kunde}")
            fahrt_destination.kunde = kunde

    zusatzinfo_str = "{}{}{}".format(
        "; " if adresse_str or kunde_str else "",
        f"; {adresse_str}" if adresse_str else "",
        f"; {kunde_str}" if kunde_str else "")

    if not dry_run and (new or len(aenderungen) > 0):
        fahrt_destination.save()
        if fahrt_destination.kunde:
            fahrt_destination.kunde.save()
        if fahrt_destination.adresse:
            fahrt_destination.adresse.save()

    if new:
        neu.append(f"Fahrt: {fahrt_mit_link(fahrt_destination, dry_run)}{zusatzinfo_str}")
    elif len(aenderungen) > 0:
        str_aenderungen = "; ".join(aenderungen)
        geaendert.append(f"Fahrt: {fahrt_mit_link(fahrt_destination)}{zusatzinfo_str}, {str_aenderungen}")
    else:
        unveraendert.append(f"Fahrt: {fahrt_mit_link(fahrt_destination)}")

    if fahrt_destination.entfernung is None:
        warnungen.append(f"Fahrt: {fahrt_mit_link(fahrt_destination, dry_run)}. Unbekannte Entfernung!")


def neue_fahrt(fahrt_source):
    fahrt_destination = Fahrt(fahrt_nr=fahrt_source['fahrt_nr'],
                              datum=fahrt_source['datum'],
                              entfernung=fahrt_source['entfernung'],
                              betrag=fahrt_source['betrag'],
                              steuer=fahrt_source['steuer'],
                              konto=fahrt_source['konto'],
                              kommentar=fahrt_source['kommentar'])

    return fahrt_destination


def check_aenderung_fahrt(fahrt_source, fahrt_destination):
    aenderungen = list()
    if fahrt_destination.fahrt_nr != fahrt_source["fahrt_nr"]:
        aenderungen.append(f"Fahrt Nr.: alt='{fahrt_destination.fahrt_nr}', neu='{fahrt_source['fahrt_nr']}'")
        fahrt_destination.fahrt_nr = fahrt_source['fahrt_nr']
    if str_datum(fahrt_destination.datum) != str_datum(fahrt_source["datum"]):
        aenderungen.append(
            f"Datum: alt='{str_datum(fahrt_destination.datum)}', neu='{str_datum(fahrt_source['datum'])}'")
        fahrt_destination.datum = fahrt_source['datum']
    if not is_empty_value(fahrt_source["entfernung"]) and str(fahrt_destination.entfernung) != str(
            fahrt_source["entfernung"]):
        # Entfernung nur auf Änderung prüfen, wenn gegegen, sonst wurde die Entfernung aus dem Kunden bzw.der Adresse
        # genommen
        aenderungen.append(f"Entfernung: alt='{fahrt_destination.entfernung}', neu='{fahrt_source['entfernung']}'")
        fahrt_destination.entfernung = fahrt_source['entfernung']
    if str(fahrt_destination.betrag) != str(fahrt_source["betrag"]):
        aenderungen.append(f"Betrag: alt='{fahrt_destination.betrag}', neu='{fahrt_source['betrag']}'")
        fahrt_destination.betrag = fahrt_source['betrag']
    if str(fahrt_destination.steuer) != str(fahrt_source["steuer"]):
        aenderungen.append(f"Steuer: alt='{fahrt_destination.steuer}', neu='{fahrt_source['steuer']}'")
        fahrt_destination.steuer = fahrt_source['steuer']
    if fahrt_destination.konto != fahrt_source["konto"]:
        aenderungen.append(f"Konto: alt='{fahrt_destination.konto}', neu='{fahrt_source['konto']}'")
        fahrt_destination.konto = fahrt_source['konto']
    kommentar_alt = fahrt_destination.kommentar or ""
    kommentar_neu = fahrt_source["kommentar"] or ""
    if kommentar_alt != kommentar_neu:
        aenderungen.append(f"Kommentar: alt='{kommentar_alt}', neu='{kommentar_neu}'")
        fahrt_destination.kommentar = kommentar_neu
    return aenderungen


def _ermittel_zeitraum(fahrten_source):
    von = datetime.datetime(3000, 12, 31)
    bis = datetime.datetime(2000, 1, 1)
    for idx, fahrt_source in enumerate(fahrten_source):
        if is_empty_value(fahrt_source["datum"]):
            raise ValueError("In der Import Datei gibt es eine Zeile in der das Datum fehlt, "
                             f"bitte in der Import Datei vervollständigen. Datensatz: {idx + 1}.")

        von = fahrt_source["datum"] if fahrt_source["datum"] < von else von
        bis = fahrt_source["datum"] if fahrt_source["datum"] > bis else bis
    return von, bis


def _kunde_aus_fahrt(fahrt):
    if fahrt.kunde is not None:
        return fahrt.kunde
    kunde = to_kunde_historisch(fahrt.kunde_historisch)
    if kunde is None:
        raise ValueError(f"Kein Kunde zur Fahrt: {str(fahrt)}")
    return kunde


def fahrt_key(datum, vorname, nachname):
    if datum is None:
        raise ValueError(f"Kein Datum: {vorname if vorname else ''} {nachname if nachname else ''}")
    return f"{datum} {vorname if vorname else ''} {nachname if nachname else ''}".strip()


def fahrt_mit_link(fahrt, ohne_link=False):
    str_fahrt = str(fahrt)
    if fahrt.kunde is None:
        str_kunde = str_kunde_historisch(fahrt.kunde_historisch, as_html=not ohne_link)
        str_fahrt += f" Kunde: {str_kunde}"
    if fahrt.adresse is None:
        str_adresse = str_adresse_historisch(fahrt.adresse_historisch, as_html=not ohne_link)
        str_fahrt += f" Adresse: {str_adresse}"
    if ohne_link:
        return str_fahrt
    url = f"/admin/fahrtenliste_main/fahrt/{fahrt.id}/change"
    link = f"<a target='_blank' href='{url}'>{str_fahrt}</a>"
    return link


def _find_eindeutigen_kunden_mit_name(fahrt_source):
    if not is_empty_value(fahrt_source["vorname"]):
        # wenn vorname und nachname gegeben, dann normale Suche über Vorname und Nachmane
        kunden = Kunde.objects.filter(vorname__iexact=fahrt_source["vorname"],
                                      nachname__iexact=fahrt_source["nachname"])
    else:
        kunden = Kunde.objects.filter(nachname__iexact=fahrt_source["nachname"])
    if len(kunden) == 1:
        return kunden[0]
    if len(kunden) > 0:
        raise ValueError(
            f"Ein Kunde in der Import Datei ist nicht eindeutig."
            f" Es existiert mehr als ein Kunde mit dem Nachnamen '{fahrt_source['nachname']}',"
            f" bitte in der Import Datei vervollständigen.")
    return None
