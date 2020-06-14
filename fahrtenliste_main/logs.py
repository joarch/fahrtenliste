import datetime
import logging

from django.conf import settings
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

LOG_ENTRY_STAUS_NEW = "new"
LOG_ENTRY_STAUS_DELETE = "delete"
LOG_ENTRY_STAUS_UPDATE = "update"

# monkey patch logging.verbose
logging.VERBOSE = settings.LOG_VERBOSE
logging.addLevelName(logging.VERBOSE, "VERBOSE")
logging.Logger.verbose = lambda inst, msg, *args, **kwargs: inst.log(logging.VERBOSE, msg, *args, **kwargs)
logging.verbose = lambda msg, *args, **kwargs: logging.log(logging.VERBOSE, msg, *args, **kwargs)

logger = logging.getLogger()
logger.setLevel(settings.LOG_LEVEL)




def log_entry_add(user, model, model_id, beschreibung, message):
    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=ContentType.objects.get(app_label="fahrtenliste_main", model=model).pk,
        object_id=model_id,
        object_repr=beschreibung,
        action_flag=ADDITION,
        change_message=message,
    )


def log_entry_change(user, model, beschreibung, message, object_id=None, action_time=None):
    content_type_id = ContentType.objects.get(app_label="fahrtenliste_main", model=model).pk

    action_time = action_time if action_time else timezone.now()

    entry = LogEntry(
        action_time=action_time,
        user_id=user.pk,
        content_type_id=content_type_id,
        object_id=object_id,
        object_repr=beschreibung,
        action_flag=CHANGE,
        change_message=message,
    )
    entry.save(force_insert=True)
    return LOG_ENTRY_STAUS_NEW, entry.id
