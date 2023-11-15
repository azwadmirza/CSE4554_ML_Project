def display_scan(scan, verbose=True):
    scan['target'] = ivre.db.db.agent.get_scan_target(scan['_id'])
    print("scan:")
    if verbose:
        print("  - id: %s" % scan['_id'])
    print("  - categories:")
    for category in scan['target'].target.infos['categories']:
        print("    - %s" % category)
    print("  - targets added: %d" % scan['target'].nextcount)
    print("  - results fetched: %d" % scan['results'])
    print("  - total targets to add: %d" % scan['target'].target.maxnbr)
    print("  - available targets: %d" % scan['target'].target.targetscount)
    if scan['target'].nextcount == scan['target'].target.maxnbr:
        print("    - all targets have been added")
    if scan['results'] == scan['target'].target.maxnbr:
        print("    - all results have been retrieved")
    if verbose:
        print("  - internal state: %r" % (scan['target'].getstate(),))
    print("  - agents:")
    for agent in scan['agents']:
        print("    - %s" % agent)