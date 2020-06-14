import os
import tempfile
import datetime

from django.conf import settings


def get_timestamp():
    return datetime.datetime.now().strftime("_%Y-%m-%d_%H%M%S")


def get_tempdir(user=None):
    if hasattr(settings, 'TEMP_DIR'):
        tempdir = settings.TEMP_DIR
    else:
        tempdir = tempfile.gettempdir()

    if user is not None:
        username = user.username
    else:
        username = "global"
    tempdir = os.path.join(tempdir, username)
    if not os.path.exists(tempdir):
        os.mkdir(tempdir)

    return tempdir
