from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from fahrtenliste_main.export_import.forms import UploadAdresseFileForm
from fahrtenliste_main.export_import.import_adresse import do_import_artikel
from fahrtenliste_main.export_import.imports import do_import


@login_required
def import_adresse(request):
    if request.method == 'POST':
        form = UploadAdresseFileForm(request.POST, request.FILES)
        if form.is_valid():
            result = do_import(do_import_artikel, request)
            return render(request, "export_import/import_export_result.html", result)
    else:
        form = UploadAdresseFileForm()
    return render(request, 'export_import/import_export.html', {'form': form})
