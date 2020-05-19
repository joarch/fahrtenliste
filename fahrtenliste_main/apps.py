from django.apps import AppConfig

import version


class FahrtenlisteConfig(AppConfig):
    name = 'fahrtenliste_main'
    verbose_name = ' Fahrtenliste'


print(f"Version: {version.VERSION}")
