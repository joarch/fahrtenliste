import json

from dateutil.parser import parse
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import format_html

from fahrtenliste_main.models import Kunde, Adresse


def str_kunde_historisch(kunde_historisch_data, as_html=True):
    try:
        data_dict = json.loads(kunde_historisch_data)
        # Adresse des Kunden laden oder entfernen, wenn die Adresse ebenfalls nicht mehr vorhanden
        # ist, das ist für die Darstellung des Kunden an dieser Stelle egal
        adresse_id = data_dict["fields"]["adresse"]
        try:
            data_dict["fields"]["adresse"] = Adresse.objects.get(id=adresse_id)
        except ObjectDoesNotExist:
            data_dict["fields"]["adresse"] = None
        kunde_historisch = Kunde(**data_dict["fields"])
        geloescht_am = parse(data_dict["geloescht_am"])
        geloescht_am = geloescht_am.strftime("%d.%m.%Y %H:%M")
        title = f"Kunde gelöscht am: {geloescht_am}"
        if as_html:
            return format_html(
                f"<span style='font-style: italic' title='{title}'>{kunde_historisch.str_kurz()}</span>")
        else:
            return kunde_historisch.str_kurz()
    except:
        if as_html:
            title = "Fehler beim Lesen des gelöschten Kunden aus dem Feld 'Kunde Historie'"
            return format_html(f"<span style='color: red' title='{title}'>Kunde gelöscht</span>")
        else:
            return "Kunde gelöscht"


def str_adresse_historisch(adresse_historisch_data, entfernung=None, as_html=True):
    try:
        data_dict = json.loads(adresse_historisch_data)
        adresse_historisch = Adresse(**data_dict["fields"])
        geloescht_am = parse(data_dict["geloescht_am"])
        geloescht_am = geloescht_am.strftime("%d.%m.%Y %H:%M")
        title = f"Adresse gelöscht am: {geloescht_am}"
        if as_html:
            return format_html(
                f"<span style='font-style: italic' title='{title}'>{adresse_historisch.str_kurz_abweichende_entfernung(entfernung)}</span>")
        else:
            return adresse_historisch.str_kurz()
    except:
        if as_html:
            title = "Fehler beim Lesen der gelöschten Adresse aus dem Feld 'Adresse Historie'"
            return format_html(f"<span style='color: red' title='{title}'>Adresse gelöscht</span>")
        else:
            return "Adresse gelöscht"


def str_adresse_entfernung_historisch(adresse_historisch_data, as_html=True):
    try:
        data_dict = json.loads(adresse_historisch_data)
        adresse_historisch = Adresse(**data_dict["fields"])
        geloescht_am = parse(data_dict["geloescht_am"])
        geloescht_am = geloescht_am.strftime("%d.%m.%Y %H:%M")
        title = f"Adresse gelöscht am: {geloescht_am}"
        if as_html:
            return format_html(
                f"<span style='font-style: italic' title='{title}'>{adresse_historisch.entfernung}</span>")
        else:
            return adresse_historisch.str_kurz()
    except:
        if as_html:
            title = "Fehler beim Lesen der gelöschten Adresse aus dem Feld 'Adresse Historie'"
            return format_html(f"<span style='color: red' title='{title}'>Adresse gelöscht</span>")
        else:
            return "Adresse gelöscht"
