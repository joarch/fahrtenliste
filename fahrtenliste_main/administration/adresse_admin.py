from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin

from fahrtenliste_main.models import Adresse


@admin.register(Adresse)
class AdresseAdmin(CompareVersionAdmin):
    list_display = ('strasse', 'plz', 'ort', 'entfernung')
    list_editable = ('entfernung',)
    readonly_fields = ('id',)
    list_filter = ('plz',)
    search_fields = ('strasse', 'plz', 'ort')
