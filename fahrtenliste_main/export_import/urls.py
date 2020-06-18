from django.conf.urls import url

from fahrtenliste_main.export_import import views

urlpatterns = [
    url(r'^import_adresse$', views.import_adresse),
    url(r'^import_kunde$', views.import_kunde),
    url(r'^import_fahrt$', views.import_fahrt)
]
