from collections import namedtuple

from django.forms import model_to_dict

from fahrtenliste_main.export_import.exports import export_nach_excel, none_mapping
from fahrtenliste_main.historisch import to_adresse_historisch

Kunde_tuple = namedtuple('adresse',
                         ['id',
                          'anrede',
                          'vorname',
                          'nachname',
                          'strasse',
                          'plz',
                          'ort',
                          'entfernung']
                         )


def export_kunden(kunden):
    kunden_data = []

    for kunde in kunden:
        kunde_dict = model_to_dict(kunde)

        _add_adresse_to_dict(kunde.adresse, kunde.adresse_historisch, kunde_dict)

        kunde_dict_filtered = {field: kunde_dict[field] for field in Kunde_tuple._fields}
        kunde_data = namedtuple('kunde', kunde_dict_filtered.keys())(**kunde_dict_filtered)

        kunden_data.append(kunde_data)

    mappings = {
        "id": none_mapping,
        "anrede": none_mapping,
        "vorname": none_mapping,
        "nachname": none_mapping,
        "strasse": none_mapping,
        "plz": none_mapping,
        "ort": none_mapping,
        "entfernung": none_mapping
    }

    return export_nach_excel(Kunde_tuple, "", kunden_data, mappings=mappings, export_name="Kunden",
                             filename_postfix="Fahrtenliste")


def _add_adresse_to_dict(adresse, adresse_historisch, kunde_dict):
    if adresse is None and adresse_historisch is not None:
        adresse = to_adresse_historisch(adresse_historisch)

    kunde_dict["strasse"] = adresse.strasse if adresse is not None else ""
    kunde_dict["plz"] = adresse.plz if adresse is not None else ""
    kunde_dict["ort"] = adresse.ort if adresse is not None else ""
    kunde_dict["entfernung"] = adresse.entfernung if adresse is not None else ""
