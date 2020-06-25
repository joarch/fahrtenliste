from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from fahrtenliste_main.export_import.forms import UploadFileForm
from fahrtenliste_main.export_import.import_adresse import do_import_adressen
from fahrtenliste_main.export_import.import_fahrt import do_import_fahrten
from fahrtenliste_main.export_import.import_kunde import do_import_kunden
from fahrtenliste_main.export_import.imports import do_import


@login_required
def import_adresse(request):
    model_objekt_name = "Adressen"
    model_objekt_url = "adresse"
    typ = "Adresse"
    return _render_oder_import(request, model_objekt_name, model_objekt_url, typ)


@login_required
def import_kunde(request):
    model_objekt_name = "Kunden"
    model_objekt_url = "kunde"
    typ = "Kunde"
    return _render_oder_import(request, model_objekt_name, model_objekt_url, typ)


@login_required
def import_fahrt(request):
    model_objekt_name = "Fahrten"
    model_objekt_url = "fahrt"
    typ = "Fahrt"
    return _render_oder_import(request, model_objekt_name, model_objekt_url, typ)


def _render_oder_import(request, model_objekt_name, model_objekt_url, typ):
    if request.method == 'POST':
        return _import(request, model_objekt_name, model_objekt_url, typ)
    else:
        return _render_import(request, model_objekt_name, model_objekt_url, typ)


def _render_import(request, model_objekt_name, model_objekt_url, typ):
    form = UploadFileForm()
    return render(request, 'import/import.html',
                  {'form': form,
                   'model_objekt_name': model_objekt_name,
                   'model_objekt_url': model_objekt_url,
                   'typ': typ,
                   'site_header': "Fahrtenliste"})


def _map_typ_to_import_fct(typ):
    if typ == 'Adresse':
        import_fct = do_import_adressen
    elif typ == 'Kunde':
        import_fct = do_import_kunden
    elif typ == 'Fahrt':
        import_fct = do_import_fahrten
    else:
        raise RuntimeError(f"Unbekannter Import Typ: '{typ}'")
    return import_fct


def _import(request, model_objekt_name, model_objekt_url, typ):
    temp_file_name = request.POST.get("temp_file_name")
    if temp_file_name is not None:
        import_fct = _map_typ_to_import_fct(typ)
        result = do_import(import_fct, model_objekt_name, model_objekt_url, request, temp_file_name)
    else:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            import_fct = _map_typ_to_import_fct(data['typ'])
            result = do_import(import_fct, model_objekt_name, model_objekt_url, request)
        else:
            messages.error(request, "Bitte eine passende Importdatei auswählen.")
            return _render_import(request, model_objekt_name, model_objekt_url, typ)
    result["model_objekt_name"] = model_objekt_name
    result["model_objekt_url"] = model_objekt_url
    result["typ"] = typ
    result["site_header"] = "Fahrtenliste"
    return render(request, "import/import_result.html", result)
