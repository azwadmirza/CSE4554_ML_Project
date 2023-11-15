    def scripts_options(self) -> None:
        """
        Parses given arguments for scripts.
        """
        self.parser.add_argument(
            '-p', '--pair',
            help='Show profits for only this pairs. Pairs are comma-separated.',
            dest='pair',
            default=None
        )