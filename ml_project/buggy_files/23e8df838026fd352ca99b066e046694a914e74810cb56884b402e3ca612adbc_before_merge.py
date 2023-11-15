    def config_args(self, parser):
        super().config_args(parser)
        parser.add_argument('--nproc', help='number of processes')