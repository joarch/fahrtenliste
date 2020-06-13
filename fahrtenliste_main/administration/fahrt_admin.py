from datetime import datetime
from threading import Semaphore

from dateutil.relativedelta import relativedelta
from django import forms
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.core.exceptions import ValidationError
from django.db.models import Max
from django.urls import path
from django.utils import formats
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from reversion_compare.admin import CompareVersionAdmin

from fahrtenliste_main.administration.fahrt_admin_report import get_von_bis_aus_request
from fahrtenliste_main.administration.fahrt_admin_report import show_report
from fahrtenliste_main.export.export import serve_export
from fahrtenliste_main.export.export_fahrt import export_fahrten
from fahrtenliste_main.models import Fahrt

semaphore_fahrt_nr = Semaphore()


class FahrtMonatFilter(SimpleListFilter):
    title = 'Zeitraum'
    parameter_name = 'zeitraum'
    value_separator = "-"
    field_names = ('datum__year', 'datum__month')

    def lookups(self, request, model_admin):
        max_datum = Fahrt.objects.aggregate(Max('datum'))['datum__max']
        if max_datum is None:
            max_datum = datetime.today()
        max_datum = datetime(max_datum.year, max_datum.month, 1)
        result = list()
        for i in range(0, 12):
            filter_datum = max_datum - relativedelta(months=i)
            str_monat_jahr = formats.date_format(filter_datum, format="YEAR_MONTH_FORMAT", use_l10n=True)

            queryset = Fahrt.objects.filter(datum__month=filter_datum.month, datum__year=filter_datum.year)
            anzahl_gesamt_im_monat = queryset.count()

            # Falls Adresse Filter aktiv, diesen ebenfalls mit bei der Anzahl in Klammern berücksichtigen
            adresse_ort_filter = request.GET.get("adresse__ort")
            if adresse_ort_filter:
                queryset = queryset.filter(adresse__ort=adresse_ort_filter)
            anzahl_getfiltert_im_monat = queryset.count()

            if anzahl_gesamt_im_monat != anzahl_getfiltert_im_monat:
                str_anzahl = f"{anzahl_getfiltert_im_monat}/{anzahl_gesamt_im_monat}"
            else:
                str_anzahl = f"{anzahl_gesamt_im_monat}"

            result.append(
                (f"{filter_datum.year}{self.value_separator}{filter_datum.month}", f"{str_monat_jahr} ({str_anzahl})"))
        return result

    def queryset(self, request, queryset):
        # wird im Java Skript Teil gemacht, da es ansonsten Überschneidungen mit den date_hierarchy Filtern kommt
        return queryset


class FahrtAdminForm(forms.ModelForm):
    class Media:
        css = {
            'all': ('pretty.css', 'css/fahrt_admin.css')
        }
        js = ('3rdparty/js/jquery-3.2.1.min.js', 'js/fahrt_admin.js',)

    def clean_entfernung(self):
        kunde = self.cleaned_data.get("kunde")
        entfernung = self.cleaned_data.get("entfernung")
        errors = list()
        if len(errors) > 0:
            raise ValidationError(errors)
        return entfernung

    def clean_adresse(self):
        kunde = self.cleaned_data.get("kunde")
        adresse = self.cleaned_data.get("adresse")
        errors = list()
        # TODO als Warnung
        # if kunde is not None:
        #    if adresse is not None and adresse != kunde.adresse:
        #        errors.append(
        #            ValidationError(
        #                "Die Adresse weicht von der aktuellen Kunden Adresse ab. "
        #                f"Bitte ändern nach {kunde.adresse}."
        #            ))
        if len(errors) > 0:
            raise ValidationError(errors)
        return adresse


@admin.register(Fahrt)
class FahrtAdmin(CompareVersionAdmin):
    change_list_template = "administration/fahrt_admin_change_list.html"
    list_display = ('fahrt_nr', 'datum', 'kunde_kurz', 'adresse_kurz', 'str_entfernung')
    list_display_links = ('fahrt_nr', 'datum', 'kunde_kurz')
    search_fields = ('kommentar',
                     'kunde__nachname', 'kunde__vorname',
                     'adresse__strasse', 'adresse__plz', 'adresse__ort',)
    readonly_fields = ('id',)
    date_hierarchy = 'datum'
    list_filter = (FahrtMonatFilter, ('adresse', RelatedDropdownFilter), ('kunde', RelatedDropdownFilter),)
    autocomplete_fields = ['kunde', 'adresse']
    form = FahrtAdminForm

    def kunde_kurz(self, obj):
        if obj.kunde is not None:
            return f"{obj.kunde.str_kurz()}"
        return ""

    kunde_kurz.admin_order_field = 'kunde__nachname'
    kunde_kurz.short_description = 'Kunde'

    def str_entfernung(self, obj):
        return obj.str_entfernung()

    str_entfernung.admin_order_field = 'entfernung'
    str_entfernung.short_description = 'Entfernung (km)'

    def adresse_kurz(self, obj):
        return obj.str_adresse_kurz()

    adresse_kurz.admin_order_field = 'adresse__strasse'
    adresse_kurz.short_description = 'Adresse'

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ['adresse', 'entfernung']
        else:
            return []

    def save_model(self, request, obj, form, change):
        if obj.kunde is not None and obj.kunde.adresse is not None:
            if obj.adresse is None:
                # Bei Neuanlage wird die Adresse vorbelegt
                obj.adresse = obj.kunde.adresse

            if obj.entfernung is None:
                # Bei Neuanlage wird die Entfernung vorbelegt
                obj.entfernung = obj.kunde.adresse.entfernung

        super(FahrtAdmin, self).save_model(request, obj, form, change)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'fahrt_nr':
            kwargs['initial'] = _get_next_fahrt_nr()
        return super(FahrtAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('report/', self.report)
        ]
        return my_urls + urls

    def report(self, request):
        return show_report(request)

    def make_export(self, request, queryset):
        von, bis = get_von_bis_aus_request(request)
        fahrten = list(queryset)
        file_path = export_fahrten(von, bis, fahrten)
        return serve_export(request, file_path)

    make_export.short_description = "Ausgewählte Fahrten exportieren"

    actions = [make_export]


def _get_next_fahrt_nr():
    semaphore_fahrt_nr.acquire()
    max = Fahrt.objects.all().aggregate(Max('fahrt_nr'))['fahrt_nr__max']
    next = int(max) + 1 if max is not None else 1
    semaphore_fahrt_nr.release()
    return next
