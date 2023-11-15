    def __init__(self):
        super(DuplicatesPlugin, self).__init__()

        self.config.add({
            'format': '',
            'count': False,
            'album': False,
            'full': False,
            'strict': False,
            'path': False,
            'keys': ['mb_trackid', 'mb_albumid'],
            'checksum': '',
            'copy': '',
            'move': '',
            'delete': False,
            'tag': '',
        })

        self._command = Subcommand('duplicates',
                                   help=__doc__,
                                   aliases=['dup'])
        self._command.parser.add_option('-c', '--count', dest='count',
                                        action='store_true',
                                        help='show duplicate counts')

        self._command.parser.add_option('-C', '--checksum', dest='checksum',
                                        action='store', metavar='PROG',
                                        help='report duplicates based on'
                                        ' arbitrary command')

        self._command.parser.add_option('-d', '--delete', dest='delete',
                                        action='store_true',
                                        help='delete items from library and '
                                        'disk')

        self._command.parser.add_option('-F', '--full', dest='full',
                                        action='store_true',
                                        help='show all versions of duplicate'
                                        ' tracks or albums')

        self._command.parser.add_option('-s', '--strict', dest='strict',
                                        action='store_true',
                                        help='report duplicates only if all'
                                        ' attributes are set')

        self._command.parser.add_option('-k', '--keys', dest='keys',
                                        action='callback', metavar='KEY1 KEY2',
                                        callback=vararg_callback,
                                        help='report duplicates based on keys')

        self._command.parser.add_option('-m', '--move', dest='move',
                                        action='store', metavar='DEST',
                                        help='move items to dest')

        self._command.parser.add_option('-o', '--copy', dest='copy',
                                        action='store', metavar='DEST',
                                        help='copy items to dest')

        self._command.parser.add_option('-t', '--tag', dest='tag',
                                        action='store',
                                        help='tag matched items with \'k=v\''
                                        ' attribute')
        self._command.parser.add_all_common_options()