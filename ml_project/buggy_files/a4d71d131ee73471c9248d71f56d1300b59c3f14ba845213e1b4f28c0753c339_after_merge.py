def split_data_line(line, dialect=None):
    delimiters = ",\t"

    # This can not be done in a per reader basis, and relational fields
    # can be HUGE
    csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))

    # Remove the line end if any
    if line[-1] == '\n':
        line = line[:-1]
    
    # Remove potential trailing whitespace
    line = line.strip()
    
    sniff_line = line

    # Add a delimiter if none is present, so that the csv.Sniffer
    # does not complain for a single-field CSV.
    if not any(d in line for d in delimiters):
        sniff_line += ","

    if dialect is None:
        dialect = csv.Sniffer().sniff(sniff_line, delimiters=delimiters)
        workaround_csv_sniffer_bug_last_field(sniff_line=sniff_line,
                                              dialect=dialect,
                                              delimiters=delimiters)

    row = next(csv.reader([line], dialect))

    return row, dialect