def _count_generic(values, table_type, type_caster):
    from pandas.core.series import Series

    values = type_caster(values)
    table = table_type(len(values))
    uniques, labels, counts = table.factorize(values)

    return Series(counts, index=uniques)