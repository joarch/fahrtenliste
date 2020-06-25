from django.contrib import admin
from django.contrib.admin import ModelAdmin
from reversion.models import Revision, Version


@admin.register(Revision)
class RevisionAdmin(ModelAdmin):
    pass


@admin.register(Version)
class VersionAdmin(ModelAdmin):
    pass
