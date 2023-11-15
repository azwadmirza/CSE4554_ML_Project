    def parse_args(self, parser, argv, environ=None):
        args = super().parse_args(parser, argv)
        args.plasma_dir = args.plasma_dir or os.environ.get('MARS_PLASMA_DIRS')
        args.spill_dir = args.spill_dir or os.environ.get('MARS_SPILL_DIRS')
        args.cache_mem = args.cache_mem or os.environ.get('MARS_CACHE_MEM_SIZE')
        args.lock_free_fileio = args.lock_free_fileio \
            or bool(int(os.environ.get('MARS_LOCK_FREE_FILEIO', '0')))
        return args