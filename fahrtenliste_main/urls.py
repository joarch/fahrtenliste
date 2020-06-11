from django.conf.urls import url

import fahrtenliste_main.views as views

urlpatterns = [
    url(r'^report_pdf', views.report_pdf)
]
