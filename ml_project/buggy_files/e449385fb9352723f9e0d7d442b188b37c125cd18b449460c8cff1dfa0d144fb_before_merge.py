    def run(self):
        # Tell pytest to omit the body of this function from tracebacks
        __tracebackhide__ = True
        database_key = str_to_bytes(fully_qualified_name(self.test))
        self.start_time = time.time()
        global in_given
        runner = ConjectureRunner(
            self.evaluate_test_data,
            settings=self.settings, random=self.random,
            database_key=database_key,
        )

        if in_given or self.collector is None:
            runner.run()
        else:  # pragma: no cover
            in_given = True
            original_trace = sys.gettrace()
            try:
                sys.settrace(None)
                runner.run()
            finally:
                in_given = False
                sys.settrace(original_trace)
        note_engine_for_statistics(runner)
        run_time = time.time() - self.start_time
        timed_out = runner.exit_reason == ExitReason.timeout
        if runner.last_data is None:
            return
        if runner.interesting_examples:
            self.falsifying_examples = sorted(
                [d for d in runner.interesting_examples.values()],
                key=lambda d: sort_key(d.buffer), reverse=True
            )
        else:
            if timed_out:
                note_deprecation((
                    'Your tests are hitting the settings timeout (%.2fs). '
                    'This functionality will go away in a future release '
                    'and you should not rely on it. Instead, try setting '
                    'max_examples to be some value lower than %d (the number '
                    'of examples your test successfully ran here). Or, if you '
                    'would prefer your tests to run to completion, regardless '
                    'of how long they take, you can set the timeout value to '
                    'hypothesis.unlimited.'
                ) % (
                    self.settings.timeout, runner.valid_examples),
                    self.settings)
            if runner.valid_examples < min(
                self.settings.min_satisfying_examples,
                self.settings.max_examples,
            ) and not (
                runner.exit_reason == ExitReason.finished and
                self.at_least_one_success
            ):
                if timed_out:
                    raise Timeout((
                        'Ran out of time before finding a satisfying '
                        'example for '
                        '%s. Only found %d examples in ' +
                        '%.2fs.'
                    ) % (
                        get_pretty_function_description(self.test),
                        runner.valid_examples, run_time
                    ))
                else:
                    raise Unsatisfiable((
                        'Unable to satisfy assumptions of hypothesis '
                        '%s. Only %d examples considered '
                        'satisfied assumptions'
                    ) % (
                        get_pretty_function_description(self.test),
                        runner.valid_examples,))

        if not self.falsifying_examples:
            return

        flaky = 0

        self.__in_final_replay = True

        for falsifying_example in self.falsifying_examples:
            self.__was_flaky = False
            try:
                with self.settings:
                    self.test_runner(
                        ConjectureData.for_buffer(falsifying_example.buffer),
                        reify_and_execute(
                            self.search_strategy, self.test,
                            print_example=True, is_final=True
                        ))
            except (UnsatisfiedAssumption, StopTest):
                report(traceback.format_exc())
                self.__flaky(
                    'Unreliable assumption: An example which satisfied '
                    'assumptions on the first run now fails it.'
                )
            except BaseException:
                if len(self.falsifying_examples) <= 1:
                    raise
                report(traceback.format_exc())
            else:
                if (
                    isinstance(
                        falsifying_example.__expected_exception,
                        DeadlineExceeded
                    ) and self.__test_runtime is not None
                ):
                    report((
                        'Unreliable test timings! On an initial run, this '
                        'test took %.2fms, which exceeded the deadline of '
                        '%.2fms, but on a subsequent run it took %.2f ms, '
                        'which did not. If you expect this sort of '
                        'variability in your test timings, consider turning '
                        'deadlines off for this test by setting deadline=None.'
                    ) % (
                        falsifying_example.__expected_exception.runtime,
                        self.settings.deadline, self.__test_runtime
                    ))
                else:
                    report(
                        'Failed to reproduce exception. Expected: \n' +
                        falsifying_example.__expected_traceback,
                    )

                filter_message = (
                    'Unreliable test data: Failed to reproduce a failure '
                    'and then when it came to recreating the example in '
                    'order to print the test data with a flaky result '
                    'the example was filtered out (by e.g. a '
                    'call to filter in your strategy) when we didn\'t '
                    'expect it to be.'
                )

                try:
                    self.test_runner(
                        ConjectureData.for_buffer(falsifying_example.buffer),
                        reify_and_execute(
                            self.search_strategy,
                            test_is_flaky(
                                self.test, self.repr_for_last_exception),
                            print_example=True, is_final=True
                        ))
                except (UnsatisfiedAssumption, StopTest):
                    self.__flaky(filter_message)
                except Flaky as e:
                    if len(self.falsifying_examples) > 1:
                        self.__flaky(e.args[0])
                    else:
                        raise

            if self.__was_flaky:
                flaky += 1

        # If we only have one example then we should have raised an error or
        # flaky prior to this point.
        assert len(self.falsifying_examples) > 1

        if flaky > 0:
            raise Flaky((
                'Hypothesis found %d distinct failures, but %d of them '
                'exhibited some sort of flaky behaviour.') % (
                    len(self.falsifying_examples), flaky))
        else:
            raise MultipleFailures((
                'Hypothesis found %d distinct failures.') % (
                    len(self.falsifying_examples,)))