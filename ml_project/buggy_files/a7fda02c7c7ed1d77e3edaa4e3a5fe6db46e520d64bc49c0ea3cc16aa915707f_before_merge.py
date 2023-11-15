def parse_facility_level(line, facility):
    facility_level = None

    if facility is not None:
        match = re.search(r'logging level {} (\S+)'.format(facility), line, re.M)
        if match:
            facility_level = match.group(1)

    return facility_level