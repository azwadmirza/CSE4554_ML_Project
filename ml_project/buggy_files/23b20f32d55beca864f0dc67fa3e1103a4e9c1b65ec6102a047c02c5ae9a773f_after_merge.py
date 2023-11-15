    def __init__(self, g_pool, source_dir='~/', destination_dir='~/'):
        super().__init__(g_pool)

        self.available_exports = []
        self.queued_exports = []
        self.active_exports = []
        self.destination_dir = os.path.expanduser(destination_dir)
        self.source_dir = os.path.expanduser(source_dir)

        self.search_task = None
        self.worker_count = cpu_count() - 1
        logger.info("Using a maximum of {} CPUs to process visualizations in parallel...".format(cpu_count() - 1))