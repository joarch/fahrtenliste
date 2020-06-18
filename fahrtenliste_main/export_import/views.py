from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from fahrtenliste_main.export_import.import_kunde import do_import_kunden
from fahrtenliste_main.export_import.forms import UploadFileForm
from fahrtenliste_main.export_import.import_adresse import do_import_adressen
from fahrtenliste_main.export_import.imports import do_import


@login_required
def import_adresse(request):
    model_objekt_name = "Adressen"
    typ = "Adresse"
    return _render_oder_import(request, model_objekt_name, typ)


@login_required
def import_kunde(request):
    model_objekt_name = "Kunden"
    typ = "Kunde"
    return _render_oder_import(request, model_objekt_name, typ)


@login_required
def import_fahrt(request):
    model_objekt_name = "Fahrten"
    typ = "Fahrt"
    return _render_oder_import(request, model_objekt_name, typ)


def _render_oder_import(request, model_objekt_name, typ):
    if request.method == 'POST':
        return _import(request, model_objekt_name, typ)
    else:
        return _render(request, model_objekt_name, typ)


def _render(request, model_objekt_name, typ):
    form = UploadFileForm()
    return render(request, 'export_import/import_export.html',
                  {'form': form, 'model_objekt_name': model_objekt_name, 'typ': typ})


def _import(request, model_objekt_name, typ):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        data = form.cleaned_data
        if data['typ'] == 'Adresse':
            import_fct = do_import_adressen
        elif data['typ'] == 'Kunde':
            import_fct = do_import_kunden
        else:
            raise RuntimeError(f"Unbekannter Import Typ: '{data['typ']}'")
        result = do_import(import_fct, request)
        return render(request, "export_import/import_export_result.html", result)
    else:
        messages.error(request, "Bitte eine passende Importdatei auswählen.")
        return _render(request, model_objekt_name, typ)
