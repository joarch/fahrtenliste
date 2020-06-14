from collections import namedtuple

from django.forms import model_to_dict

from fahrtenliste_main.export_import.exports import export_nach_excel, none_mapping

Adresse_tuple = namedtuple('adresse',
                           ['id',
                            'strasse',
                            'plz',
                            'ort',
                            'entfernung']
                           )


def export_adressen(adressen):
    fahrten_data = []

    for adresse in adressen:
        adresse_dict = model_to_dict(adresse)
        adresse_dict_filtered = {field: adresse_dict[field] for field in Adresse_tuple._fields}
        adresse_data = namedtuple('adresse', adresse_dict_filtered.keys())(**adresse_dict_filtered)
        fahrten_data.append(adresse_data)

    mappings = {
        "id": none_mapping,
        "plz": none_mapping,
        "ort": none_mapping,
        "strasse": none_mapping,
        "entfernung": none_mapping
    }

    return export_nach_excel(Adresse_tuple, "", fahrten_data, mappings=mappings, export_name="Adressen",
                             filename_postfix="Fahrtenliste")
