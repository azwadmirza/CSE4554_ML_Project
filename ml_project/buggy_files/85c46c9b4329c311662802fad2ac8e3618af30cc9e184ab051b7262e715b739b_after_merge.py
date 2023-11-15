def get_packages(installed, regex):
    pat = re.compile(regex, re.I) if regex else None
    for dist in sorted(installed, key=lambda x: x.lower()):
        name = name_dist(dist)
        if pat and pat.search(name) is None:
            continue

        yield dist