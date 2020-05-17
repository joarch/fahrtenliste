from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin

from fahrtenliste_main.models import Einstellung


@admin.register(Einstellung)
class EinstellungAdmin(CompareVersionAdmin):
    list_display = ('name', 'wert')
    search_fields = ('name',)

    def wert(self, obj):
        return obj.wert

    wert.short_description = 'Wert'
