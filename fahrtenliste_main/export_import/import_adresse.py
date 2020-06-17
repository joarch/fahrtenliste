import datetime
import os

import reversion

from fahrtenliste_main.export_import.excel import is_empty_value
from fahrtenliste_main.export_import.imports import import_von_excel
from fahrtenliste_main.models import Adresse
from fahrtenliste_main.temp_dir import get_tempdir
from temp_dir import get_timestamp

IMPORT_FORMAT_ADRESSE_STANDARD = {
    "id": "fahrtenliste",
    "typ": "Adressen",
    "name": "Fahrtenliste",
    "beschreibung": "Fahrtenliste Standard Format",
    "filemuster": "Fahrtenliste_Adressen_.*\\.xlsx",
    "start_row": 2,
    "columns":
        {
            "A": "id",
            "B": "strasse",
            "C": "plz",
            "D": "ort",
            "E": "entfernung"
        }
}

IMPORT_FORMATE_ADRESSE = {
    IMPORT_FORMAT_ADRESSE_STANDARD["id"]: IMPORT_FORMAT_ADRESSE_STANDARD
}


def do_import_adressen(user, file, format_key, dry_run=True):
    import_format = IMPORT_FORMATE_ADRESSE.get(format_key)
    if import_format is None:
        raise RuntimeError(f"Unbekanntes Import Format '{format_key}'!")

    with reversion.create_revision():
        reversion.set_user(user)
        reversion.set_comment("Import Artikel ({}): {}".format(import_format["name"], file.name))
        return _import_adressen(user, file, import_format, dry_run)


def _import_adressen(user, file, import_format, dry_run, tempfile_mit_timestamp=False):
    neu = list()
    geloescht = list()
    geaendert = list()
    unveraendert = list()
    warnung = list()
    adressen_in_source = list()

    filename, file_extension = os.path.splitext(file.name)
    temp_dir = get_tempdir(user)
    timestamp = get_timestamp() if tempfile_mit_timestamp else ""
    temp_file = "{}_{}{}".format(filename, timestamp, file_extension)
    temp_file_path = os.path.join(temp_dir, temp_file)
    with open(temp_file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    adressen_source = import_von_excel(temp_file_path, import_format)

    adressen_source_ohne_id = list(filter(lambda a: is_empty_value(a["id"]), adressen_source))
    adressen_source_mit_id = list(filter(lambda a: not is_empty_value(a["id"]), adressen_source))
    adressen_source_by_id = {a["id"]: a for a in adressen_source_mit_id}

    adressen_destination = Adresse.objects.filter()
    adressen_destination_by_id = {a.id: a for a in adressen_destination}
    adressen_destination_by_key = {_key(a.strasse, a.plz, a.ort): a for a in adressen_destination}

    # alle Adressen ohne Id Spalte (in der Regel neue Adressen)
    for adresse_source in adressen_source_ohne_id:
        key = _key(adresse_source["strasse"], adresse_source["plz"], adresse_source["ort"])
        adresse_destination = adressen_destination_by_key.get(key)
        if adresse_destination is None:
            _neue_adresse(adresse_source, neu, dry_run)
        elif adresse_destination is not None:
            adressen_in_source.append(adresse_destination)
            _check_aenderung(adresse_source, adresse_destination, geaendert, unveraendert, dry_run)

    # alle Adressen mit Id Spalte
    for id, adresse_source in adressen_source_by_id.items():
        # Suche mit Id
        adresse_destination = adressen_destination_by_id.get(id)

        if adresse_destination is None:
            # wenn nicht über Id gefunden Suchen über Key (Strasse, PLZ und Ort)
            key = _key(adresse_source["strasse"], adresse_source["plz"], adresse_source["ort"])
            adresse_destination = adressen_destination_by_key.get(key)

        if adresse_destination is None:
            _neue_adresse(adresse_source, neu, dry_run)
        elif adresse_destination is not None:
            adressen_in_source.append(adresse_destination)
            _check_aenderung(adresse_source, adresse_destination, geaendert, unveraendert, dry_run)

    # Warnungen bei Adressen, die nicht mehr in der Liste stehen
    # Hinweis: es werden keine Adressen automatisch gelöscht
    for id, adresse_destination in adressen_destination_by_id.items():
        if adresse_destination not in adressen_in_source:
            warnung.append(f"fehlt im Import: {_adresse_mit_link(adresse_destination)}")

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


def _neue_adresse(adresse_source, neu, dry_run):
    adresse_destination = Adresse(strasse=adresse_source['strasse'], plz=adresse_source['plz'],
                                  ort=adresse_source['ort'], entfernung=adresse_source['entfernung'])
    if not dry_run:
        adresse_destination.save()
    neu.append(f"{_adresse_mit_link(adresse_destination)}")


def _check_aenderung(adresse_source, adresse_destination, geaendert, unveraendert, dry_run):
    aenderung = list()
    if adresse_destination.strasse != adresse_source["strasse"]:
        aenderung.append(f"- Straße: alt='{adresse_destination.stasse}', neu='{adresse_source['strasse']}'")
        adresse_destination.strasse = adresse_source['strasse']
    if adresse_destination.plz != adresse_source["plz"]:
        aenderung.append(f"- Plz: alt='{adresse_destination.plz}', neu='{adresse_source['plz']}'")
        adresse_destination.plz = adresse_source['plz']
    if adresse_destination.ort != adresse_source["ort"]:
        aenderung.append(f"- Ort: alt='{adresse_destination.ort}', neu='{adresse_source['ort']}'")
        adresse_destination.ort = adresse_source['ort']
    if adresse_destination.entfernung != adresse_source["entfernung"]:
        aenderung.append(
            f"- Entfernung: alt='{adresse_destination.entfernung}', neu='{adresse_source['entfernung']}'")
        adresse_destination.entfernung = adresse_source['entfernung']

    if len(aenderung) > 0:
        aenderung_detail = "\n".join(aenderung)
        geaendert.append(f"{_adresse_mit_link(adresse_destination)}\n{aenderung_detail}")
        if not dry_run:
            adresse_destination.save()
    else:
        unveraendert.append(f"{_adresse_mit_link(adresse_destination)}")


def _key(strasse, plz, ort):
    return f"{strasse} {plz} {ort}"


def _adresse_mit_link(adresse):
    url = f"/admin/fahrtenliste_main/adresse/{adresse.id}/change"
    link = f"<a target='_blank' href='{url}'>{adresse}</a>"
    return link
