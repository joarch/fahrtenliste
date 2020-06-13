from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin

from fahrtenliste_main.export.export import serve_export
from fahrtenliste_main.export.export_kunde import export_kunden
from fahrtenliste_main.models import Kunde


@admin.register(Kunde)
class KundeAdmin(CompareVersionAdmin):
    list_display = ('nachname', 'vorname', 'adresse', 'entfernung')
    readonly_fields = ('id',)
    search_fields = ('nachname', 'vorname', 'adresse__strasse', 'adresse__plz', 'adresse__ort',)
    autocomplete_fields = ['adresse']

    def entfernung(self, obj):
        if obj.adresse is not None:
            return f"{obj.adresse.entfernung} km"
        return "-"

    def make_export(self, request, queryset):
        kunden = list(queryset)
        file_path = export_kunden(kunden)
        return serve_export(request, file_path)

    make_export.short_description = "Ausgewählte Kunden exportieren"

    actions = [make_export]
