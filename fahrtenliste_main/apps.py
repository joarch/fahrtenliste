from django.apps import AppConfig

import fahrtenliste_main.version

class FahrtenlisteConfig(AppConfig):
    name = 'fahrtenliste_main'
    verbose_name = ' Fahrtenliste'

print("***************************")
print(f"Version: {fahrtenliste_main.version.VERSION}")
print("***************************")
