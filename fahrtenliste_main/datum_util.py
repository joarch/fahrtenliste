from datetime import date, datetime, timedelta


def get_jahr_von_bis(year):
    von = datetime(year, 1, 1)
    bis = datetime(year, 12, 31)
    return von, bis


def get_monat_von_bis(datum):
    von = datetime(datum.year, datum.month, 1)
    if datum.month == 12:
        bis = datetime(datum.year + 1, 1, 1)
    else:
        bis = datetime(datum.year, datum.month + 1, 1)
    bis = bis - timedelta(days=1)
    return von, bis


def str_datum(datum):
    if type(datum) == date:
        return datum.strftime("%d.%m.%Y")
    if type(datum) == datetime:
        return datum.strftime("%d.%m.%Y")
    if type(datum) == str:
        return datum
