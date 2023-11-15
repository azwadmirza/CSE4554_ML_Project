def pretty_package(dist, pkg):
    from ..utils import human_bytes

    pkg = dump_record(pkg)
    d = OrderedDict([
        ('file name', dist.to_filename()),
        ('name', pkg['name']),
        ('version', pkg['version']),
        ('build string', pkg['build']),
        ('build number', pkg['build_number']),
        ('channel', dist.channel),
        ('size', human_bytes(pkg['size'])),
    ])
    for key in sorted(set(pkg.keys()) - SKIP_FIELDS):
        d[key] = pkg[key]

    print()
    header = "%s %s %s" % (d['name'], d['version'], d['build string'])
    print(header)
    print('-'*len(header))
    for key in d:
        print("%-12s: %s" % (key, d[key]))
    print('dependencies:')
    for dep in pkg['depends']:
        print('    %s' % dep)