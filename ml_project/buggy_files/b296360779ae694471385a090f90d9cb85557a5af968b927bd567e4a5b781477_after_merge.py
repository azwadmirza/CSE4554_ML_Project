def value_to_display(value, truncate=False, trunc_len=80, minmax=False):
    """Convert value for display purpose"""
    try:
        if isinstance(value, recarray):
            fields = value.names
            display = 'Field names: ' + ', '.join(fields)
        elif isinstance(value, MaskedArray):
            display = 'Masked array'
        elif minmax and isinstance(value, ndarray):
            if value.size == 0:
                display = repr(value)
            try:
                display = 'Min: %r\nMax: %r' % (value.min(), value.max())
            except TypeError:
                pass
            except ValueError:
                # Happens when one of the array cell contains a sequence
                pass
        elif isinstance(value, ndarray):
            display = repr(value)
        elif isinstance(value, (list, tuple, dict, set)):
            display = CollectionsRepr.repr(value)
        elif isinstance(value, Image):
            display = '%s  Mode: %s' % (address(value), value.mode)
        elif isinstance(value, DataFrame):
            cols = value.columns
            if PY2 and len(cols) > 0:
                # Get rid of possible BOM utf-8 data present at the
                # beginning of a file, which gets attached to the first
                # column header when headers are present in the first
                # row.
                # Fixes Issue 2514
                try:
                    ini_col = to_text_string(cols[0], encoding='utf-8-sig')
                except:
                    ini_col = to_text_string(cols[0])
                cols = [ini_col] + [to_text_string(c) for c in cols[1:]]
            else:
                cols = [to_text_string(c) for c in cols]
            display = 'Column names: ' + ', '.join(list(cols))
        elif isinstance(value, NavigableString):
            # Fixes Issue 2448
            display = to_text_string(value)
        elif is_binary_string(value):
            try:
                display = to_text_string(value, 'utf8')
            except:
                display = value
        elif is_text_string(value):
            display = value
        elif isinstance(value, NUMERIC_TYPES) or isinstance(value, bool) or \
          isinstance(value, datetime.date):
            display = repr(value)
        else:
            # Note: Don't trust on repr's. They can be inefficient and
            # so freeze Spyder quite easily
            # display = repr(value)
            type_str = to_text_string(type(value))
            display = type_str[1:-1]
            if truncate and len(display) > trunc_len:
                display = display[:trunc_len].rstrip() + ' ...'
    except:
        type_str = to_text_string(type(value))
        display = type_str[1:-1]

    return display