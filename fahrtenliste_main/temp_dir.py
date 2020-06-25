import datetime
import logging
import os
import tempfile
from os import listdir
from os.path import isfile, join
from stat import S_ISREG, ST_CTIME, ST_MODE

from django.conf import settings

logger = logging.getLogger(__name__)
del logging


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


def clean_temp_dir(file_count, temp_dir, temp_file, filename_match=None):
    if filename_match is None:
        split = temp_file.split("_")
        filename_match = split[0] if len(split) > 0 else tempfile

    files_to_delete = [f for f in listdir(temp_dir) if isfile(join(temp_dir, f)) and f.startswith(filename_match)]
    # Sortierung nach Datum: https://stackoverflow.com/a/539024
    # get all entries in the directory w/ stats
    files_to_delete = (os.path.join(temp_dir, fn) for fn in files_to_delete)
    files_to_delete = ((os.stat(path), path) for path in files_to_delete)
    # leave only regular files, insert creation date
    files_to_delete = ((stat[ST_CTIME], path)
                       for stat, path in files_to_delete if S_ISREG(stat[ST_MODE]))
    # NOTE: on Windows `ST_CTIME` is a creation date
    #  but on Unix it could be something else
    # NOTE: use `ST_MTIME` to sort by a modification dat
    files_to_delete = sorted(files_to_delete, reverse=True)

    number_of_files_to_delete = len(files_to_delete) - file_count
    if number_of_files_to_delete <= 0:
        return

    number_deleted = 0
    for cdate, path in sorted(files_to_delete):
        if number_deleted >= number_of_files_to_delete:
            break
        number_deleted += 1
        os.remove(join(temp_dir, path))
        logger.debug(f'Temporäre Datei gelöscht: "{join(temp_dir, path)}"')


def get_temp_file_path(user, temp_file_name):
    """
    Gibt den vollständigen Pfad der Tempdatei zurück.
    """
    temp_dir = get_tempdir(user)
    temp_file_path = os.path.join(temp_dir, temp_file_name)
    if not os.path.exists(temp_file_path):
        raise RuntimeError("Die temporäre Datei existiert nicht mehr.")
    return temp_file_path


def write_to_temp_file(user, file, tempfile_mit_timestamp=False):
    """
    Schreibt das übergebene File in das Temp Verzeichnis.
    Gibt den Namen der Temp-Datei zurück.
    """
    filename, file_extension = os.path.splitext(file.name)
    temp_dir = get_tempdir(user)
    timestamp = "_{}".format(get_timestamp()) if tempfile_mit_timestamp else ""
    temp_file = "{}{}{}".format(filename, timestamp, file_extension)
    temp_file_path = os.path.join(temp_dir, temp_file)

    clean_temp_dir(10, temp_dir, temp_file)

    with open(temp_file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return temp_file_path
