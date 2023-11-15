    def __init__(self, max_length, draw_bytes):
        self.max_length = max_length
        self.is_find = False
        self._draw_bytes = draw_bytes
        self.overdraw = 0
        self.level = 0
        self.block_starts = {}
        self.blocks = []
        self.buffer = bytearray()
        self.output = u''
        self.status = Status.VALID
        self.frozen = False
        global global_test_counter
        self.testcounter = global_test_counter
        global_test_counter += 1
        self.start_time = benchmark_time()
        self.events = set()
        self.forced_indices = set()
        self.forced_blocks = set()
        self.capped_indices = {}
        self.interesting_origin = None
        self.tags = set()
        self.draw_times = []
        self.__intervals = None

        self.examples = []
        self.example_stack = []
        self.has_discards = False

        self.start_example(TOP_LABEL)