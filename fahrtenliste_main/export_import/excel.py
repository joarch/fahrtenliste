def is_empty_value(value):
    if value is None:
        return True
    if isinstance(value, str):
        return len(value) == 0
    return False


def is_empty(ws, row, column):
    try:
        value = ws.cell(row=row, column=column).value
        return is_empty_value(value)
    except ValueError:
        return True


def get_cell_value(ws, row, column):
    if is_empty(ws, row, column):
        return None
    return ws.cell(row=row, column=column).value


def to_row(cell):
    return int(cell[1:]) - 1
