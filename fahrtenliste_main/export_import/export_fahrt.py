from collections import namedtuple

from django.forms import model_to_dict

from fahrtenliste_main.export_import.exports import export_nach_excel, none_mapping
from historisch import to_kunde_historisch, to_adresse_historisch

Fahrt_tuple = namedtuple('fahrt',
                         ['id',
                          'fahrt_nr',
                          'datum',
                          'anrede',
                          'vorname',
                          'nachname',
                          'strasse',
                          'plz',
                          'ort',
                          'entfernung',
                          'betrag',
                          'steuer',
                          'konto',
                          'kommentar'])


def export_fahrten(von, bis, fahrten):
    fahrten_data = []

    for fahrt in fahrten:
        fahrt_dict = model_to_dict(fahrt)

        _add_adresse_to_dict(fahrt.adresse, fahrt.adresse_historisch, fahrt_dict)
        _add_kunde_to_dict(fahrt.kunde, fahrt.kunde_historisch, fahrt_dict)

        fahrt_dict_filtered = {field: fahrt_dict[field] for field in Fahrt_tuple._fields}
        fahrt_data = namedtuple('fahrt', fahrt_dict_filtered.keys())(**fahrt_dict_filtered)
        fahrten_data.append(fahrt_data)

    if von is not None and bis is not None:
        detailname = "Zeitraum: {} bis {}".format(von.strftime("%d.%m.%Y"), bis.strftime("%d.%m.%Y"))
    else:
        detailname = ""

    mappings = {
        "id": none_mapping,
        "fahrt_nr": none_mapping,
        'anrede': none_mapping,
        'vorname': none_mapping,
        'nachname': none_mapping,
        'strasse': none_mapping,
        'plz': none_mapping,
        'ort': none_mapping,
        "entfernung": none_mapping,
        "betrag": none_mapping,
        "steuer": none_mapping,
        "konto": none_mapping,
        "kommentar": none_mapping
    }
    return export_nach_excel(Fahrt_tuple, detailname, fahrten_data, mappings=mappings, export_name="Fahrten",
                             filename_postfix="Fahrtenliste")


def _add_kunde_to_dict(kunde, kunde_historisch, fahrt_dict):
    if kunde is None and kunde_historisch is not None:
        kunde = to_kunde_historisch(kunde_historisch)

    fahrt_dict["anrede"] = kunde.anrede if kunde is not None else ""
    fahrt_dict["vorname"] = kunde.vorname if kunde is not None else ""
    fahrt_dict["nachname"] = kunde.nachname if kunde is not None else ""


def _add_adresse_to_dict(adresse, adresse_historisch, kunde_dict):
    if adresse is None and adresse_historisch is not None:
        adresse = to_adresse_historisch(adresse_historisch)

    kunde_dict["strasse"] = adresse.strasse if adresse is not None else ""
    kunde_dict["plz"] = adresse.plz if adresse is not None else ""
    kunde_dict["ort"] = adresse.ort if adresse is not None else ""
