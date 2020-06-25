from django.contrib import admin
from django.contrib.admin import AdminSite

from fahrtenliste_main.administration import adresse_admin
from fahrtenliste_main.administration import einstellung_admin
from fahrtenliste_main.administration import fahrt_admin
from fahrtenliste_main.administration import kunde_admin
from fahrtenliste_main.administration import log_entry_admin

#Django-Reversion Model Admin standardmaessig nicht angezeigt
#from fahrtenliste_main.administration import reversion_admin

admin.site.site_title = "Verwaltung"
admin.site.site_header = "Fahrtenliste"
admin.site.index_title = "Fahrtenliste"
