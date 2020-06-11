import os

from django.contrib.auth.decorators import login_required
from django.views.static import serve

from fahrtenliste_main.administration.fahrt_admin_report import create_report_pdf


@login_required
def report_pdf(request):
    filename = create_report_pdf(request)
    return serve(request, os.path.basename(filename), os.path.dirname(filename))
