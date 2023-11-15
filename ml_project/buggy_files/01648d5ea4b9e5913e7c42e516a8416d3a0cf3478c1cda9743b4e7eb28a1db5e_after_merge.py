    def __init__(self, test_runner, search_strategy, test, settings, random):
        self.test_runner = test_runner
        self.search_strategy = search_strategy
        self.settings = settings
        self.at_least_one_success = False
        self.last_exception = None
        self.falsifying_examples = ()
        self.__was_flaky = False
        self.random = random
        self.__warned_deadline = False
        self.__existing_collector = None
        self.__test_runtime = None

        self.test = test

        self.coverage_data = CoverageData()
        self.files_to_propagate = set()

        if settings.use_coverage and not IN_COVERAGE_TESTS:  # pragma: no cover
            if Collector._collectors:
                self.hijack_collector(Collector._collectors[-1])

            self.collector = Collector(
                branch=True,
                timid=FORCE_PURE_TRACER,
                should_trace=self.should_trace,
                check_include=hypothesis_check_include,
                concurrency='thread',
                warn=escalate_warning,
            )
            self.collector.reset()

            # Hide the other collectors from this one so it doesn't attempt to
            # pause them (we're doing trace function management ourselves so
            # this will just cause problems).
            self.collector._collectors = []
        else:
            self.collector = None