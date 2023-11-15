    def add_options(self, parser):
        super(Command, self).add_options(parser)
        parser.remove_option("--headers")