    def config_args(self, parser):
        super().config_args(parser)
        parser.add_argument('--cpu-procs', help='number of processes used for cpu')
        parser.add_argument('--cuda-device', help='CUDA device to use, if not specified, will '
                                                  'use CPU only')
        parser.add_argument('--net-procs', help='number of processes used for networking')
        parser.add_argument('--io-procs', help=argparse.SUPPRESS,
                            action=arg_deprecated_action('--net-procs'))
        parser.add_argument('--phy-mem', help='physical memory size limit')
        parser.add_argument('--ignore-avail-mem', action='store_true', help='ignore available memory')
        parser.add_argument('--cache-mem', help='cache memory size limit')
        parser.add_argument('--min-mem', help='minimal free memory required to start worker')
        parser.add_argument('--spill-dir', help='spill directory')
        parser.add_argument('--lock-free-fileio', action='store_true',
                            help='make file io lock free, add this when using a mounted dfs')
        parser.add_argument('--plasma-dir', help='path of plasma directory. When specified, the size '
                                                 'of plasma store will not be taken into account when '
                                                 'managing host memory')

        compress_types = ', '.join(v.value for v in CompressType.__members__.values())
        parser.add_argument('--disk-compression',
                            default=options.worker.disk_compression,
                            help='compression type used for disks, '
                                 'can be selected from %s. %s by default'
                                 % (compress_types, options.worker.disk_compression))
        parser.add_argument('--transfer-compression',
                            default=options.worker.transfer_compression,
                            help='compression type used for network transfer, '
                                 'can be selected from %s. %s by default'
                                 % (compress_types, options.worker.transfer_compression))