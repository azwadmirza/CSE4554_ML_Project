def inspect_main(argv):
    # type: (List[unicode]) -> None
    """Debug functionality to print out an inventory"""
    if len(argv) < 1:
        print("Print out an inventory file.\n"
              "Error: must specify local path or URL to an inventory file.",
              file=sys.stderr)
        sys.exit(1)

    class MockConfig(object):
        intersphinx_timeout = None  # type: int
        tls_verify = False

    class MockApp(object):
        srcdir = ''
        config = MockConfig()

        def warn(self, msg):
            print(msg, file=sys.stderr)

    filename = argv[0]
    invdata = fetch_inventory(MockApp(), '', filename)  # type: ignore
    for key in sorted(invdata or {}):
        print(key)
        for entry, einfo in sorted(invdata[key].items()):
            print('\t%-40s %s%s' % (entry,
                                    einfo[3] != '-' and '%-40s: ' % einfo[3] or '',
                                    einfo[2]))