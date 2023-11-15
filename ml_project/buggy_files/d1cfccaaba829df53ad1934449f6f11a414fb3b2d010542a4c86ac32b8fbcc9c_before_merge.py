    def range(cls, columns, dimension):
        column = columns.data[columns.get_dimension(dimension).name]
        if column.dtype.kind == 'O':
            column = np.sort(column[column.notnull()].compute())
            return column[0], column[-1]
        else:
            return dd.compute(column.min(), column.max())