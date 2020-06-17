from datetime import date
from datetime import datetime
from decimal import Decimal


def json_serial(obj):
    if isinstance(obj, datetime) or isinstance(obj, date):
        serial = obj.isoformat()
        return serial
    if isinstance(obj, Decimal):
        serial = map_decimal(obj)
        return serial
    raise TypeError("Type not serializable {}".format(type(obj)))


def map_decimal(value, decimal_places=2, zero_blank=False):
    if value is None:
        return ""
    if type(value) == str:
        value_str = value
    else:
        format_pattern = "{0:,." + str(decimal_places) + "f}"
        value_str = format_pattern.format(value)
    if zero_blank and value == Decimal(0):
        return ""
    return value_str.replace(',', ' ').replace('.', ',').replace(' ', '.')


def to_bool(value):
    """konvertiert value in den passenden Boolean Wert.
    Referenz: http://stackoverflow.com/questions/715417/converting-from-a-string-to-boolean-in-python

    :param value: zu konvertierenden Wert
    :return: Boolean Wert
    """
    valid = {'true': True, 't': True, '1': True, 'on': True,
             'false': False, 'f': False, '0': False, 'off': False
             }
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if not isinstance(value, str):
        raise ValueError('invalid literal for boolean. Not a string.')
    lower_value = value.lower()
    if lower_value in valid:
        return valid[lower_value]
    else:
        raise ValueError('invalid literal for boolean: "%s"' % value)
