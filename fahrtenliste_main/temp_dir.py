import datetime
import os
import tempfile

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


def write_to_temp_file(user, file, tempfile_mit_timestamp=False):
    """
    Schreibt das übergebene File in das Temp Verzeichnis.
    Gibt den Namen der Temp-Datei zurück.
    """
    filename, file_extension = os.path.splitext(file.name)
    temp_dir = get_tempdir(user)
    timestamp = get_timestamp() if tempfile_mit_timestamp else ""
    temp_file = "{}_{}{}".format(filename, timestamp, file_extension)
    temp_file_path = os.path.join(temp_dir, temp_file)
    with open(temp_file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return temp_file_path
