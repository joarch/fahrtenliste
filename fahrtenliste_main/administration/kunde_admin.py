from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin

from fahrtenliste_main.administration.historisch import adresse_entfernung_historisch
from fahrtenliste_main.administration.historisch import str_adresse_historisch
from fahrtenliste_main.export_import.export_kunde import export_kunden
from fahrtenliste_main.export_import.exports import serve_export
from fahrtenliste_main.models import Kunde


@admin.register(Kunde)
class KundeAdmin(CompareVersionAdmin):
    list_display = ('nachname', 'vorname', 'adresse_kurz', 'entfernung')
    list_display_links = ('nachname', 'vorname')
    readonly_fields = ('id', 'adresse_historisch')
    search_fields = ('nachname', 'vorname', 'adresse__strasse', 'adresse__plz', 'adresse__ort',)
    autocomplete_fields = ['adresse']

    def entfernung(self, obj):
        if obj.adresse is not None:
            return f"{obj.adresse.entfernung} km"
        if obj.adresse_historisch is not None:
            return adresse_entfernung_historisch(obj.adresse_historisch)
        return ""

    def adresse_kurz(self, obj):
        if obj.adresse is not None:
            return f"{obj.adresse.str_kurz()} km"
        if obj.adresse_historisch is not None:
            return str_adresse_historisch(obj.adresse_historisch)
        return ""

    def make_export(self, request, queryset):
        kunden = list(queryset)
        file_path = export_kunden(kunden)
        return serve_export(request, file_path)

    make_export.short_description = "Ausgewählte Kunden exportieren"

    actions = [make_export]
