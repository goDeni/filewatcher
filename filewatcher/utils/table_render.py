from collections import OrderedDict

L_UPP_ANGLE = '┌'
L_DOWN_ANGLE = '└'
R_UPP_ANGLE = '┐'
R_DOWN_ANGLE = '┘'
LINE_C_DOWN = '┬'
LINE_C_UPP = '┴'
LINE_H = '─'
LINE_W = '│'


class TableRender:
    def __init__(self):
        self.table = OrderedDict()
        self.column_lens = OrderedDict()

    def add_column(self, name: str):
        self.table[name] = []
        self.column_lens[name] = len(name)

    def write_in_column(self, column_name: str, value):
        if not isinstance(value, str) and value is not None:
            value = str(value)

        if column_name not in self.table:
            self.add_column(column_name)

        self.table[column_name].append(value)
        self.column_lens[column_name] = max(self.column_lens[column_name], len(value or ''))

    def render(self) -> str:
        table = L_UPP_ANGLE

        table += LINE_C_DOWN.join(column_name.center(self.column_lens[column_name], LINE_H)
                                  for column_name in self.table) + R_UPP_ANGLE + '\n'

        for num_row in range(max(len(column) for column in self.table.values())):
            row = LINE_W.join((rows[num_row] or '').ljust(self.column_lens[name_column])
                              for name_column, rows in self.table.items())
            table += LINE_W + row + LINE_W + '\n'

        down_row = L_DOWN_ANGLE + LINE_C_UPP.join(value * LINE_H for value in self.column_lens.values()) + R_DOWN_ANGLE

        table = table + down_row
        return table
