    def add_arguments(self, parser):
        parser.add_argument('slugs', nargs='+', type=str)

        parser.add_argument(
            '-r',
            action='store_true',
            dest='record',
            default=False,
            help='Make a Build',
        )

        parser.add_argument(
            '-f',
            action='store_true',
            dest='force',
            default=False,
            help='Force a build in sphinx',
        )

        parser.add_argument(
            '-V',
            dest='version',
            default=None,
            help='Build a version, or all versions',
        )