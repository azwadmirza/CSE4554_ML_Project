    def __init__(self, cache_timeout=60):
        """Init the class to collect stats about processes."""
        # Add internals caches because psutil do not cache all the stats
        # See: https://code.google.com/p/psutil/issues/detail?id=462
        self.username_cache = {}
        self.cmdline_cache = {}

        # The internals caches will be cleaned each 'cache_timeout' seconds
        self.cache_timeout = cache_timeout
        self.cache_timer = Timer(self.cache_timeout)

        # Init the io dict
        # key = pid
        # value = [ read_bytes_old, write_bytes_old ]
        self.io_old = {}

        # Init stats
        self.auto_sort = None
        self._sort_key = None
        # Default processes sort key is 'auto'
        # Can be overwrite from the configuration file (issue#1536) => See glances_processlist.py init
        self.set_sort_key('auto', auto=True)
        self.processlist = []
        self.reset_processcount()

        # Tag to enable/disable the processes stats (to reduce the Glances CPU consumption)
        # Default is to enable the processes stats
        self.disable_tag = False

        # Extended stats for top process is enable by default
        self.disable_extended_tag = False

        # Test if the system can grab io_counters
        try:
            p = psutil.Process()
            p.io_counters()
        except Exception as e:
            logger.warning('PsUtil can not grab processes io_counters ({})'.format(e))
            self.disable_io_counters = True
        else:
            logger.debug('PsUtil can grab processes io_counters')
            self.disable_io_counters = False

        # Test if the system can grab gids
        try:
            p = psutil.Process()
            p.gids()
        except Exception as e:
            logger.warning('PsUtil can not grab processes gids ({})'.format(e))
            self.disable_gids = True
        else:
            logger.debug('PsUtil can grab processes gids')
            self.disable_gids = False

        # Maximum number of processes showed in the UI (None if no limit)
        self._max_processes = None

        # Process filter is a regular expression
        self._filter = GlancesFilter()

        # Whether or not to hide kernel threads
        self.no_kernel_threads = False

        # Store maximums values in a dict
        # Used in the UI to highlight the maximum value
        self._max_values_list = ('cpu_percent', 'memory_percent')
        # { 'cpu_percent': 0.0, 'memory_percent': 0.0 }
        self._max_values = {}
        self.reset_max_values()