from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin

from fahrtenliste_main.export_import.exports import serve_export
from fahrtenliste_main.export_import.export_adresse import export_adressen
from fahrtenliste_main.models import Adresse


@admin.register(Adresse)
class AdresseAdmin(CompareVersionAdmin):
    list_display = ('strasse', 'plz', 'ort', 'entfernung')
    list_display_links = ('strasse', 'plz', 'ort')
    list_editable = ('entfernung',)
    readonly_fields = ('id',)
    list_filter = ('plz',)
    search_fields = ('strasse', 'plz', 'ort')
    change_list_template = 'administration/adresse_admin_change_list_mit_import.html'

    def make_export(self, request, queryset):
        adressen = list(queryset)
        file_path = export_adressen(adressen)
        return serve_export(request, file_path)

    make_export.short_description = "Ausgewählte Adressen exportieren"

    actions = [make_export]
