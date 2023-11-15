    def __init__(self, test_runner, search_strategy, test, settings, random):
        self.test_runner = test_runner
        self.search_strategy = search_strategy
        self.settings = settings
        self.at_least_one_success = False
        self.last_exception = None
        self.repr_for_last_exception = None
        self.falsifying_examples = ()
        self.__was_flaky = False
        self.random = random
        self.__warned_deadline = False
        self.__existing_collector = None
        self.__test_runtime = None
        self.__in_final_replay = False

        if self.settings.deadline is None:
            self.test = test
        else:
            @proxies(test)
            def timed_test(*args, **kwargs):
                self.__test_runtime = None
                start = time.time()
                result = test(*args, **kwargs)
                runtime = (time.time() - start) * 1000
                self.__test_runtime = runtime
                if self.settings.deadline is not_set:
                    if (
                        not self.__warned_deadline and
                        runtime >= 200
                    ):
                        self.__warned_deadline = True
                        note_deprecation((
                            'Test took %.2fms to run. In future the default '
                            'deadline setting will be 200ms, which will '
                            'make this an error. You can set deadline to '
                            'an explicit value of e.g. %d to turn tests '
                            'slower than this into an error, or you can set '
                            'it to None to disable this check entirely.') % (
                                runtime, ceil(runtime / 100) * 100,
                        ))
                elif runtime >= self.current_deadline:
                    raise DeadlineExceeded(runtime, self.settings.deadline)
                return result
            self.test = timed_test

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