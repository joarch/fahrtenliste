from collections import namedtuple

from django.forms import model_to_dict

from fahrtenliste_main.export_import.exports import export_nach_excel, none_mapping

Fahrt_tuple = namedtuple('fahrt',
                         ['id',
                          'fahrt_nr',
                          'datum',
                          'adresse',
                          'kunde',
                          'entfernung',
                          'betrag',
                          'steuer',
                          'konto',
                          'kommentar'])


def export_fahrten(von, bis, fahrten):
    fahrten_data = []

    for fahrt in fahrten:
        fahrt_dict = model_to_dict(fahrt)
        fahrt_dict["kunde"] = fahrt.kunde.str_kurz() if fahrt.kunde is not None else ""
        fahrt_dict["adresse"] = fahrt.adresse.str_kurz() if fahrt.adresse is not None else ""
        fahrt_dict_filtered = {field: fahrt_dict[field] for field in Fahrt_tuple._fields}
        fahrt_data = namedtuple('fahrt', fahrt_dict_filtered.keys())(**fahrt_dict_filtered)
        fahrten_data.append(fahrt_data)

    detailname = "Zeitraum: {} bis {}".format(von.strftime("%d.%m.%Y"), bis.strftime("%d.%m.%Y"))

    mappings = {
        "id": none_mapping,
        "fahrt_nr": none_mapping,
        "adresse": none_mapping,
        "kunde": none_mapping,
        "entfernung": none_mapping,
        "betrag": none_mapping,
        "steuer": none_mapping,
        "konto": none_mapping,
        "kommentar": none_mapping
    }
    return export_nach_excel(Fahrt_tuple, detailname, fahrten_data, mappings=mappings, export_name="Fahrten",
                             filename_postfix="Fahrtenliste")
