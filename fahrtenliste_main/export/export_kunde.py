from collections import namedtuple

from django.forms import model_to_dict

from fahrtenliste_main.export.export import export_nach_excel, none_mapping

Kunde_tuple = namedtuple('adresse',
                         ['anrede',
                          'vorname',
                          'nachname',
                          'adresse']
                         )


def export_kunden(kunden):
    kunden_data = []

    for kunde in kunden:
        kunde_dict = model_to_dict(kunde)
        kunde_dict["adresse"] = kunde.adresse.str_kurz() if kunde.adresse is not None else ""
        kunde_dict_filtered = {field: kunde_dict[field] for field in Kunde_tuple._fields}
        kunde_data = namedtuple('kunde', kunde_dict_filtered.keys())(**kunde_dict_filtered)
        kunden_data.append(kunde_data)

    mappings = {
        "anrede": none_mapping,
        "vorname": none_mapping,
        "nachname": none_mapping,
        "adresse": none_mapping
    }

    return export_nach_excel(Kunde_tuple, "", kunden_data, mappings=mappings, export_name="Kunden")
