    def __init__(self, g_pool):
        super().__init__(g_pool)

        # initialize empty menu
        # and load menu configuration of last session
        self.menu = None

        self.exports = []
        self.new_exports = []
        self.active_exports = []
        default_path = os.path.expanduser('~/work/pupil/recordings/demo')
        self.destination_dir = default_path
        self.source_dir = default_path

        self.run = False
        self.workers = [None for x in range(mp.cpu_count())]
        logger.info("Using a maximum of {} CPUs to process visualizations in parallel...".format(mp.cpu_count()))