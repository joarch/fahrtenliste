from django.conf.urls import url
from django.urls import include

import fahrtenliste_main.views as views

urlpatterns = [
    url(r'^report_pdf', views.report_pdf),
    url(r'^export_import/', include('fahrtenliste_main.export_import.urls')),
]
