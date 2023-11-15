def replace_logical_line(lines, logical, idx, n):
    """Replaces lines at idx that may end in line continuation with a logical
    line that spans n lines.
    """
    if n == 1:
        lines[idx] = logical
        return
    space = ' '
    for i in range(idx, idx+n-1):
        a = len(lines[i])
        b = logical.find(space, a-1)
        if b < 0:
            # no space found
            lines[i] = logical
            logical = ''
        else:
            # found space to split on
            lines[i] = logical[:b] + str(LINE_CONTINUATION)
            logical = logical[b:]
    lines[idx+n-1] = logical