import os
from datetime import datetime

from django.conf import settings
from django.shortcuts import render

from fahrtenliste_main.einstellung import get_einstellung
from fahrtenliste_main.datum_util import get_jahr_von_bis, get_monat_von_bis
from fahrtenliste_main.report_fahrt import get_report_data
from fahrtenliste_main.report_fahrt_pdf import pdf_report


def _get_temp_dir():
    temp_dir = settings.TEMP_DIR
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    return temp_dir


def get_von_bis_aus_request(request):
    tag = _param_to_int(request, "datum__day")
    monat = _param_to_int(request, "datum__month")
    jahr = _param_to_int(request, "datum__year")
    return _get_zeitraum_von_bis(tag, monat, jahr)


def create_report_pdf(request):
    tag = _param_to_int(request, "datum__day")
    monat = _param_to_int(request, "datum__month")
    jahr = _param_to_int(request, "datum__year")
    von, bis = _get_zeitraum_von_bis(tag, monat, jahr)
    kilometerpauschale_faktor = get_einstellung(settings.EINSTELLUNG_NAME_KILOMETERPAUSCHALE)
    name_im_report = get_einstellung(settings.EINSTELLUNG_NAME)
    data = get_report_data(von, bis, kilometerpauschale_faktor, name_im_report)

    return pdf_report(_get_temp_dir(), data)


def show_report(request):
    tag = _param_to_int(request, "datum__day")
    monat = _param_to_int(request, "datum__month")
    jahr = _param_to_int(request, "datum__year")
    von, bis = _get_zeitraum_von_bis(tag, monat, jahr)
    kilometerpauschale_faktor = get_einstellung(settings.EINSTELLUNG_NAME_KILOMETERPAUSCHALE)
    name_im_report = get_einstellung(settings.EINSTELLUNG_NAME)
    data = get_report_data(von, bis, kilometerpauschale_faktor, name_im_report)

    # Url um zur Liste der Fahrten zurückzukehren
    url_params = list()
    if tag:
        url_params.append("datum__day=" + request.GET.get("datum__day"))
    if monat:
        url_params.append("datum__month=" + request.GET.get("datum__month"))
    if jahr:
        url_params.append("datum__year=" + request.GET.get("datum__year"))
    data["fahrten_url"] = "/admin/fahrtenliste_main/fahrt/"
    if len(url_params) > 0:
        data["fahrten_url"] += "?" + "&".join(url_params)

    return render(request, 'administration/report_fahrten.html', {"data": data})


def _get_zeitraum_von_bis(tag, monat, jahr):
    # Report Zeitraum von-bis auf Basis von Tag, Monat und Jahr ermitteln
    if tag is not None:
        # Tages Report
        if monat is None or jahr is None:
            raise RuntimeError("Monat und Jahr ist unbekannt!")
        datum = datetime(jahr, monat, tag)
        von, bis = datum, datum
    elif monat is not None:
        # Monatsreport
        if jahr is None:
            raise RuntimeError("Monat und Jahr ist unbekannt!")
        datum = datetime(jahr, monat, 1)
        von, bis = get_monat_von_bis(datum)
    elif jahr is not None:
        # Jahresreport
        von, bis = get_jahr_von_bis(jahr)
    else:
        # Monatsreport aktueller Monat, wenn keine Parameter übergeben werden
        von, bis = get_monat_von_bis(datetime.today())
    return von, bis


def _param_to_int(request, param_name):
    value = request.GET.get(param_name)
    if value == "null":
        return None
    elif value is None:
        return None
    else:
        return int(value)
