from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.admin.models import LogEntry, DELETION, CHANGE, ADDITION
from django.utils.safestring import mark_safe


@admin.register(LogEntry)
class LogEntryAdmin(ModelAdmin):
    list_display = ["action_time", "user", "icon_action_flag", "content_type", "object_repr",
                    "change_message"]
    ordering = ('-action_time',)

    def icon_action_flag(self, obj):
        # Icon was gemacht wurde, gelöscht, geändert oder hinzugefügt
        src = ""
        alt = ""
        if obj.action_flag == DELETION:
            src = "/static/images/icon_deletelink.gif"
            alt = "Gelöscht"
        elif obj.action_flag == CHANGE:
            src = "/static/images/icon_changelink.gif"
            alt = "Geändert"
        elif obj.action_flag == ADDITION:
            src = "/static/images/icon_addlink.gif"
            alt = "Hinzugefügt"
        return mark_safe("<img src='%s' alt='%s'/>" % (src, alt))
