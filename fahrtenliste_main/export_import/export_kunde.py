from collections import namedtuple

from django.forms import model_to_dict

from fahrtenliste_main.export_import.exports import export_nach_excel, none_mapping
from fahrtenliste_main.historisch import str_adresse_entfernung_historisch

Kunde_tuple = namedtuple('adresse',
                         ['id',
                          'anrede',
                          'vorname',
                          'nachname',
                          'adresse']
                         )


def export_kunden(kunden):
    kunden_data = []

    for kunde in kunden:
        kunde_dict = model_to_dict(kunde)
        if kunde.adresse is not None:
            kunde_dict["adresse"] = kunde.adresse.str_kurz()
        elif kunde.adresse_historisch is not None:
            kunde_dict["adresse"] = str_adresse_entfernung_historisch(kunde.adresse_historisch, as_html=False)

        kunde_dict_filtered = {field: kunde_dict[field] for field in Kunde_tuple._fields}
        kunde_data = namedtuple('kunde', kunde_dict_filtered.keys())(**kunde_dict_filtered)

        kunden_data.append(kunde_data)

    mappings = {
        "id": none_mapping,
        "anrede": none_mapping,
        "vorname": none_mapping,
        "nachname": none_mapping,
        "adresse": none_mapping
    }

    return export_nach_excel(Kunde_tuple, "", kunden_data, mappings=mappings, export_name="Kunden",
                             filename_postfix="Fahrtenliste")
