from django.core.exceptions import ObjectDoesNotExist

from fahrtenliste_main.models import Einstellung


def get_einstellung(name):
    try:
        return Einstellung.objects.get(name=name).wert
    except ObjectDoesNotExist:
        raise RuntimeError(f"Die Einstellung '{name}' existiert nicht, bitte in den Einstellungen hinzufügen.")
