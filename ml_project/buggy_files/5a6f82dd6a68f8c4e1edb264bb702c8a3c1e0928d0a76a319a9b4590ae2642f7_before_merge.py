def get_outputs():
    """ Return list of tuples containing output name and geometry """
    outputs = list()
    for line in get_vidmodes():
        parts = line.split()
        if len(parts) < 2:
            continue
        if parts[1] == 'connected':
            geom = parts[2] if parts[2] != 'primary' else parts[3]
            if geom.startswith('('):  # Screen turned off, no geometry
                continue
            outputs.append((parts[0], geom))
    return outputs