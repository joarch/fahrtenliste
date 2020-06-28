import datetime
import os

import reversion

from fahrtenliste_main.export_import.excel import is_empty_value
from fahrtenliste_main.export_import.imports import import_von_excel
from fahrtenliste_main.models import Adresse
from fahrtenliste_main.temp_dir import write_to_temp_file
from fahrtenliste_main.temp_dir import get_temp_file_path

IMPORT_FORMAT_ADRESSE_STANDARD = {
    "id": "fahrtenliste",
    "typ": "Adresse",
    "name": "Fahrtenliste Adresse",
    "beschreibung": "Fahrtenliste Standard Format Adresse",
    "filemuster": "Fahrtenliste_Adressen_.*\\.xlsx",
    "start_row": 2,
    "nicht_im_import_aktion": "WARNUNG",
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


def do_import_adressen(user, file, format_key, dry_run=True, temp_file_name=None):
    import_format = IMPORT_FORMATE_ADRESSE.get(format_key)
    if import_format is None:
        raise RuntimeError(f"Unbekanntes Import Format '{format_key}'!")

    file_name = file.name if file is not None else temp_file_name

    if dry_run:
        return _import_adressen(user, file, import_format, dry_run, temp_file_name)
    else:
        with reversion.create_revision():
            reversion.set_user(user)
            reversion.set_comment("Import Adressen ({}): {}".format(import_format["name"], file_name))
            return _import_adressen(user, file, import_format, dry_run, temp_file_name=temp_file_name)


def _import_adressen(user, file, import_format, dry_run, tempfile_mit_timestamp=False, temp_file_name=None):
    neu = list()
    geloescht = list()
    geaendert = list()
    unveraendert = list()
    warnung = list()
    adressen_in_source = list()

    file_name = file.name if file is not None else temp_file_name

    if temp_file_name is None:
        temp_file_path = write_to_temp_file(user, file, tempfile_mit_timestamp)
        temp_file_name = os.path.basename(temp_file_path)
    else:
        if file is not None:
            raise RuntimeError("Fehler In-Memory-File und temp_file_name übergeben.")
        temp_file_path = get_temp_file_path(user, temp_file_name)

    adressen_source = import_von_excel(temp_file_path, import_format)

    adressen_source_ohne_id = list(filter(lambda a: is_empty_value(a["id"]), adressen_source))
    adressen_source_mit_id = list(filter(lambda a: not is_empty_value(a["id"]), adressen_source))
    adressen_source_by_id = {a["id"]: a for a in adressen_source_mit_id}

    adressen_destination = Adresse.objects.filter()
    adressen_destination_by_id = {a.id: a for a in adressen_destination}
    adressen_destination_by_key = {adresse_key(a.strasse, a.plz, a.ort): a for a in adressen_destination}

    # alle Adressen ohne Id Spalte (in der Regel neue Adressen)
    for adresse_source in adressen_source_ohne_id:
        key = adresse_key(adresse_source["strasse"], adresse_source["plz"], adresse_source["ort"])
        adresse_destination = adressen_destination_by_key.get(key)
        if adresse_destination is None:
            neue_adresse(adresse_source, neu, dry_run)
        else:
            adressen_in_source.append(adresse_destination)
            check_aenderung_adresse(adresse_source, adresse_destination, geaendert, unveraendert, dry_run)

    # alle Adressen mit Id Spalte
    for id, adresse_source in adressen_source_by_id.items():
        # Suche mit Id
        adresse_destination = adressen_destination_by_id.get(id)

        if adresse_destination is None:
            # wenn nicht über Id gefunden Suchen über Key (Strasse, PLZ und Ort)
            key = adresse_key(adresse_source["strasse"], adresse_source["plz"], adresse_source["ort"])
            adresse_destination = adressen_destination_by_key.get(key)

        if adresse_destination is None:
            neue_adresse(adresse_source, neu, dry_run)
        else:
            adressen_in_source.append(adresse_destination)
            check_aenderung_adresse(adresse_source, adresse_destination, geaendert, unveraendert, dry_run)

    nicht_im_import_aktion = import_format["nicht_im_import_aktion"]
    if nicht_im_import_aktion == "WARNUNG":
        # Warnungen bei Adressen, die nicht mehr in der Liste stehen
        # Hinweis: es werden keine Adressen automatisch gelöscht
        for id, adresse_destination in adressen_destination_by_id.items():
            if adresse_destination not in adressen_in_source:
                warnung.append(f"fehlt im Import: {adresse_mit_link(adresse_destination)}")
    elif nicht_im_import_aktion == "NICHTS":
        pass
    else:
        raise RuntimeError(f"Unbekannte 'nicht_im_import_aktion': '{nicht_im_import_aktion}'")

    return {
        "format": "{}".format(import_format["name"]),
        "beschreibung": "{}".format(import_format["beschreibung"]),
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


def neue_adresse(adresse_source, neu, dry_run):
    adresse_destination = Adresse(strasse=adresse_source['strasse'], plz=adresse_source['plz'],
                                  ort=adresse_source['ort'], entfernung=adresse_source['entfernung'])
    if not dry_run:
        adresse_destination.save()
    neu.append(f"Adresse: {adresse_mit_link(adresse_destination, dry_run)}")
    return adresse_destination


def check_aenderung_adresse(adresse_source, adresse_destination, geaendert, unveraendert, dry_run):
    aenderung = list()
    if adresse_destination.strasse != adresse_source["strasse"]:
        aenderung.append(f"Straße: alt='{adresse_destination.stasse}', neu='{adresse_source['strasse']}'")
        adresse_destination.strasse = adresse_source['strasse']
    if str(adresse_destination.plz) != str(adresse_source["plz"]):
        aenderung.append(f"Plz: alt='{adresse_destination.plz}', neu='{adresse_source['plz']}'")
        adresse_destination.plz = adresse_source['plz']
    if adresse_destination.ort != adresse_source["ort"]:
        aenderung.append(f"Ort: alt='{adresse_destination.ort}', neu='{adresse_source['ort']}'")
        adresse_destination.ort = adresse_source['ort']
    if str(adresse_destination.entfernung) != str(adresse_source["entfernung"]):
        aenderung.append(
            f"Entfernung: alt='{adresse_destination.entfernung}', neu='{adresse_source['entfernung']}'")
        adresse_destination.entfernung = adresse_source['entfernung']

    if len(aenderung) > 0:
        aenderung_detail = "; ".join(aenderung)
        geaendert.append(f"Adresse: {adresse_mit_link(adresse_destination)}; {aenderung_detail}")
        if not dry_run:
            adresse_destination.save()
    else:
        unveraendert.append(f"Adresse: {adresse_mit_link(adresse_destination)}")


def adresse_key(strasse, plz, ort):
    return f"{strasse if strasse else ''} {plz if plz else ''} {ort if ort else ''}".strip()


def adresse_mit_link(adresse, ohne_link=False):
    if ohne_link:
        return str(adresse)
    url = f"/admin/fahrtenliste_main/adresse/{adresse.id}/change"
    link = f"<a target='_blank' href='{url}'>{adresse}</a>"
    return link
