import datetime

import reversion

from fahrtenliste_main.export_import.excel import is_empty_value
from fahrtenliste_main.export_import.import_adresse import check_aenderung_adresse, neue_adresse, adresse_mit_link, \
    adresse_key
from fahrtenliste_main.export_import.imports import import_von_excel
from fahrtenliste_main.models import Kunde, Adresse
from fahrtenliste_main.temp_dir import write_to_temp_file

IMPORT_FORMAT_KUNDE_STANDARD = {
    "id": "fahrtenliste",
    "typ": "Kunde",
    "name": "Fahrtenliste Kunde",
    "beschreibung": "Fahrtenliste Standard Format Kunde",
    "filemuster": "Fahrtenliste_Kunden_.*\\.xlsx",
    "start_row": 2,
    "columns":
        {
            "A": "id",
            "B": "anrede",
            "C": "vorname",
            "D": "nachname",
            "E": "strasse",
            "F": "plz",
            "G": "ort",
            "H": "entfernung"
        }
}

IMPORT_FORMATE_KUNDE = {
    IMPORT_FORMAT_KUNDE_STANDARD["id"]: IMPORT_FORMAT_KUNDE_STANDARD
}


def do_import_kunden(user, file, format_key, dry_run=True):
    import_format = IMPORT_FORMATE_KUNDE.get(format_key)
    if import_format is None:
        raise RuntimeError(f"Unbekanntes Import Format '{format_key}'!")

    with reversion.create_revision():
        reversion.set_user(user)
        reversion.set_comment("Import Kunde ({}): {}".format(import_format["name"], file.name))
        return _import_kunden(user, file, import_format, dry_run)


def _import_kunden(user, file, import_format, dry_run, tempfile_mit_timestamp=False):
    neu = list()
    geloescht = list()
    geaendert = list()
    unveraendert = list()
    warnung = list()
    kunden_in_source = list()

    temp_file_path = write_to_temp_file(user, file, tempfile_mit_timestamp)

    kunden_source = import_von_excel(temp_file_path, import_format)
    kunden_source_ohne_id = list(filter(lambda k: is_empty_value(k["id"]), kunden_source))
    kunden_source_mit_id = list(filter(lambda k: not is_empty_value(k["id"]), kunden_source))
    kunden_source_by_id = {k["id"]: k for k in kunden_source_mit_id}

    kunden_destination = Kunde.objects.filter()
    kunden_destination_by_id = {k.id: k for k in kunden_destination}
    kunden_destination_by_key = {kunde_key(k.vorname, k.nachname): k for k in kunden_destination}

    adressen_destination = Adresse.objects.filter()
    adressen_destination_by_key = {adresse_key(a.strasse, a.plz, a.ort): a for a in adressen_destination}

    # alle Kunden ohne Id Spalte (in der Regel neue Kunden)
    for kunde_source in kunden_source_ohne_id:
        key = kunde_key(kunde_source["vorname"], kunde_source["nachname"])
        kunde_destination = kunden_destination_by_key.get(key)
        if kunde_destination is None:
            kunde_destination = neuer_kunde(kunde_source, neu, dry_run)
            new = True
            change = False
        else:
            kunden_in_source.append(kunde_destination)
            new = False
            change = _check_aenderung(kunde_source, kunde_destination, geaendert, unveraendert, dry_run)

        key_adresse = adresse_key(kunde_source["strasse"], kunde_source["plz"], kunde_source["ort"])

        # Adresse zum Kunden
        if kunde_destination.adresse is None and key_adresse:
            adresse = adressen_destination_by_key.get(key_adresse)
            neu_str = ""
            if adresse is None:
                # neue Adresse
                neu_str = " (neue Adresse)"
                adresse = neue_adresse(kunde_source, neu if not new else [], dry_run)
                adressen_destination_by_key[adresse_key] = adresse
            kunde_destination.adresse = adresse
            if not dry_run:
                kunde_destination.save()
            if new:
                neu.pop()
                neu.append(f"Kunde: {kunde_mit_link(kunde_destination, dry_run)}")
            else:
                if not change:
                    # wenn Kunde nicht geändert Info über Adressen Änderung ausgeben
                    geaendert.append(
                        f"Kunde: {kunde_mit_link(kunde_destination)}; Adresse: {adresse_mit_link(adresse)}{neu_str}")
                else:
                    # wenn Kunde geändert Adresse als Detail anhängen
                    geaendert.append(f"; Adresse: {adresse_mit_link(adresse)}{neu_str}")
        elif kunde_destination.adresse is None and not key_adresse:
            # vorher und nachher keine Adresse
            pass
        else:
            check_aenderung_adresse(kunde_source, kunde_destination.adresse, geaendert, [], dry_run)

    # TODO Kunden mit ID Spalte


    # Warnungen bei Kunden, die nicht mehr in der Liste stehen
    # Hinweis: es werden keine Kunden automatisch gelöscht
    for id, kunde_destination in kunden_destination_by_id.items():
        if kunde_destination not in kunden_in_source:
            warnung.append(f"fehlt im Import: {kunde_mit_link(kunde_destination)}")

    return {
        "format": "{}".format(import_format["name"]),
        "beschreibung": "{}".format(import_format["beschreibung"]),
        "filename": file.name,
        "timestamp": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "neu": neu,
        "geloescht": geloescht,
        "geaendert": geaendert,
        "unveraendert": unveraendert,
        "warnung": warnung,
        "simulation": "ja" if dry_run else "nein",
    }


def neuer_kunde(kunde_source, neu, dry_run):
    kunde_destination = Kunde(anrede=kunde_source['anrede'], vorname=kunde_source['vorname'],
                              nachname=kunde_source['nachname'])
    if not dry_run:
        kunde_destination.save()
    neu.append(f"Kunde: {kunde_mit_link(kunde_destination, dry_run)}")
    return kunde_destination


def _check_aenderung(kunde_source, kunde_destination, geaendert, unveraendert, dry_run):
    aenderung = list()
    if kunde_destination.anrede != kunde_source["anrede"]:
        aenderung.append(f"Anrede: alt='{kunde_destination.anrede}', neu='{kunde_source['anrede']}'")
        kunde_destination.anrede = kunde_source['anrede']
    if kunde_destination.vorname != kunde_source["vorname"]:
        aenderung.append(f"Vorname: alt='{kunde_destination.vorname}', neu='{kunde_source['vorname']}'")
        kunde_destination.vorname = kunde_source['vorname']
    if kunde_destination.nachname != kunde_source["nachname"]:
        aenderung.append(f"Nachname: alt='{kunde_destination.nachname}', neu='{kunde_source['nachname']}'")
        kunde_destination.nachname = kunde_source['nachname']

    adresse_neu_hinzugekommen = kunde_destination.adresse is None and adresse_key(kunde_source["strasse"],
                                                                                  kunde_source["plz"],
                                                                                  kunde_source["ort"])

    if len(aenderung) > 0:
        aenderung_detail = "; ".join(aenderung)
        geaendert.append(f"Kunde: {kunde_mit_link(kunde_destination)}\n{aenderung_detail}")
        if not dry_run:
            kunde_destination.save()
        return True
    elif not adresse_neu_hinzugekommen:
        # keine Änderung und Adresse nicht neu hinzugekommen
        unveraendert.append(f"Kunde: {kunde_mit_link(kunde_destination)}")
    return False


def kunde_key(vorname, nachname):
    return f"{vorname if vorname else ''} {nachname if nachname else ''}".strip()


def kunde_mit_link(kunde, ohne_link=False):
    if ohne_link:
        return str(kunde)
    url = f"/admin/fahrtenliste_main/kunde/{kunde.id}/change"
    link = f"<a target='_blank' href='{url}'>{kunde}</a>"
    return link
