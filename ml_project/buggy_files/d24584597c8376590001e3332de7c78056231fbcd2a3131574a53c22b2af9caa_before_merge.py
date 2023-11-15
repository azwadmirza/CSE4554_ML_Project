def parse_egg_info(path):
    """
    Parse an .egg-info file and return its canonical distribution name
    """
    info = {}
    for line in open(path):
        line = line.strip()
        m = pat.match(line)
        if m:
            key = m.group(1).lower()
            info[key] = m.group(2)
        try:
            return '%(name)s-%(version)s-<egg_info>' % info
        except KeyError:
            pass
    return None