def _create_parser():
    parser = _argparse.ArgumentParser(
        prog=NAME.lower(),
        add_help=False,
        epilog='For details on individual actions, run `%s <action> --help`.' % NAME.lower()
    )
    subparsers = parser.add_subparsers(title='actions', help='optional action to perform')

    sp = subparsers.add_parser('show', help='show information about devices')
    sp.add_argument(
        'device',
        nargs='?',
        default='all',
        help='device to show information about; may be a device number (1..6), a serial, '
        'a substring of a device\'s name, or "all" (the default)'
    )
    sp.set_defaults(action='show')

    sp = subparsers.add_parser('probe', help='probe a receiver (debugging use only)')
    sp.add_argument('receiver', nargs='?', help='select a certain receiver when more than one is present')
    sp.set_defaults(action='probe')

    sp = subparsers.add_parser(
        'config',
        help='read/write device-specific settings',
        epilog='Please note that configuration only works on active devices.'
    )
    sp.add_argument(
        'device',
        help='device to configure; may be a device number (1..6), a device serial, '
        'or at least 3 characters of a device\'s name'
    )
    sp.add_argument('setting', nargs='?', help='device-specific setting; leave empty to list available settings')
    sp.add_argument('value_key', nargs='?', help='new value for the setting or key for keyed settings')
    sp.add_argument('extra_subkey', nargs='?', help='value for keyed or subkey for subkeyed settings')
    sp.add_argument('extra2', nargs='?', help='value for subkeyed settings')
    sp.set_defaults(action='config')

    sp = subparsers.add_parser(
        'pair',
        help='pair a new device',
        epilog='The Logitech Unifying Receiver supports up to 6 paired devices at the same time.'
    )
    sp.add_argument('receiver', nargs='?', help='select a certain receiver when more than one is present')
    sp.set_defaults(action='pair')

    sp = subparsers.add_parser('unpair', help='unpair a device')
    sp.add_argument(
        'device', help='device to unpair; may be a device number (1..6), a serial, '
        'or a substring of a device\'s name.'
    )
    sp.set_defaults(action='unpair')

    return parser, subparsers.choices