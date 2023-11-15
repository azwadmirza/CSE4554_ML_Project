def parse_facility_level(line, facility, dest):
    facility_level = None

    if dest == 'server':
        match = re.search(r'logging server (?:\S+) (\d+)', line, re.M)
        if match:
            facility_level = match.group(1)

    elif facility is not None:
        match = re.search(r'logging level {} (\S+)'.format(facility), line, re.M)
        if match:
            facility_level = match.group(1)

    return facility_level