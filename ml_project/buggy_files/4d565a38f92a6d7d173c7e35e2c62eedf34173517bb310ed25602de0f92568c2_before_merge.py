def get_logical_line(lines, idx):
    """Returns a single logical line (i.e. one without line continuations)
    from a list of lines.  This line should begin at index idx. This also
    returns the number of physical lines the logical line spans. The lines
    should not contain newlines
    """
    n = 1
    nlines = len(lines)
    line = lines[idx]
    while line.endswith('\\') and idx < nlines:
        n += 1
        idx += 1
        line = line[:-1] + lines[idx]
    return line, n