    def add_arguments(self, parser):
        parser.add_argument('--interval', action='store', dest='interval',
                            help='Number of minutes to wait after a successful ping before the next ping.')
        parser.add_argument('--checkrate', action='store', dest='checkrate',
                            help='Number of minutes to wait between failed ping attempts.')
        parser.add_argument('--server', action='store', dest='server',
                            help='Base URL of the server to connect to.')