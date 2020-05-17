from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin

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
