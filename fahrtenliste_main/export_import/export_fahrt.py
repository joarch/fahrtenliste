from collections import namedtuple

from django.forms import model_to_dict

from fahrtenliste_main.export_import.exports import export_nach_excel, none_mapping
from fahrtenliste_main.historisch import str_adresse_entfernung_historisch, str_kunde_historisch

Fahrt_tuple = namedtuple('fahrt',
                         ['id',
                          'fahrt_nr',
                          'datum',
                          'kunde',
                          'adresse',
                          'entfernung',
                          'betrag',
                          'steuer',
                          'konto',
                          'kommentar'])


def export_fahrten(von, bis, fahrten):
    fahrten_data = []

    for fahrt in fahrten:
        fahrt_dict = model_to_dict(fahrt)

        if fahrt.kunde is not None:
            fahrt_dict["kunde"] = fahrt.kunde.str_kurz()
        elif fahrt.kunde_historisch is not None:
            fahrt_dict["kunde"] = str_kunde_historisch(fahrt.kunde_historisch, as_html=False)
        if fahrt.adresse is not None:
            fahrt_dict["adresse"] = fahrt.adresse.str_kurz()
        elif fahrt.adresse_historisch is not None:
            fahrt_dict["adresse"] = str_adresse_entfernung_historisch(fahrt.adresse_historisch, as_html=False)

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
        "kunde": none_mapping,
        "adresse": none_mapping,
        "entfernung": none_mapping,
        "betrag": none_mapping,
        "steuer": none_mapping,
        "konto": none_mapping,
        "kommentar": none_mapping
    }
    return export_nach_excel(Fahrt_tuple, detailname, fahrten_data, mappings=mappings, export_name="Fahrten",
                             filename_postfix="Fahrtenliste")
