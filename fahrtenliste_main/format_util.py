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
