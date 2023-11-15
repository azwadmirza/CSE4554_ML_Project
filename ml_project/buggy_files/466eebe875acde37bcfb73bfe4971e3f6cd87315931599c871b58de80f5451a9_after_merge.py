    def parse_args(self, parser, argv, environ=None):
        args = super().parse_args(parser, argv)
        environ = environ or os.environ

        args.plasma_dir = args.plasma_dir or environ.get('MARS_PLASMA_DIRS')
        args.spill_dir = args.spill_dir or environ.get('MARS_SPILL_DIRS')
        args.cache_mem = args.cache_mem or environ.get('MARS_CACHE_MEM_SIZE')
        args.disable_proc_recover = args.disable_proc_recover \
            or bool(int(environ.get('MARS_DISABLE_PROC_RECOVER', '0')))
        args.io_parallel_num = args.io_parallel_num \
            or int(environ.get('MARS_IO_PARALLEL_NUM', '1'))
        if args.io_parallel_num == 1 and bool(int(environ.get('MARS_LOCK_FREE_FILEIO', '0'))):
            args.io_parallel_num = 2 ** 16
        return args