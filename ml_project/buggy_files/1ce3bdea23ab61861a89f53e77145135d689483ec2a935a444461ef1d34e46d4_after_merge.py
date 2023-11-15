    def generate_new_examples(self):
        if Phase.generate not in self.settings.phases:
            return
        if self.interesting_examples:
            # The example database has failing examples from a previous run,
            # so we'd rather report that they're still failing ASAP than take
            # the time to look for additional failures.
            return

        zero_data = self.cached_test_function(hbytes(self.settings.buffer_size))
        if zero_data.status > Status.OVERRUN:
            self.__data_cache.pin(zero_data.buffer)

        if zero_data.status == Status.OVERRUN or (
            zero_data.status == Status.VALID
            and len(zero_data.buffer) * 2 > self.settings.buffer_size
        ):
            fail_health_check(
                self.settings,
                "The smallest natural example for your test is extremely "
                "large. This makes it difficult for Hypothesis to generate "
                "good examples, especially when trying to reduce failing ones "
                "at the end. Consider reducing the size of your data if it is "
                "of a fixed size. You could also fix this by improving how "
                "your data shrinks (see https://hypothesis.readthedocs.io/en/"
                "latest/data.html#shrinking for details), or by introducing "
                "default values inside your strategy. e.g. could you replace "
                "some arguments with their defaults by using "
                "one_of(none(), some_complex_strategy)?",
                HealthCheck.large_base_example,
            )

        if zero_data is not Overrun:
            # If the language starts with writes of length >= cap then there is
            # only one string in it: Everything after cap is forced to be zero (or
            # to be whatever value is written there). That means that once we've
            # tried the zero value, there's nothing left for us to do, so we
            # exit early here.
            has_non_forced = False

            # It's impossible to fall out of this loop normally because if we
            # did then that would mean that all blocks are writes, so we would
            # already have triggered the exhaustedness check on the tree and
            # finished running.
            for b in zero_data.blocks:  # pragma: no branch
                if b.start >= self.cap:
                    break
                if not b.forced:
                    has_non_forced = True
                    break
            if not has_non_forced:
                self.exit_with(ExitReason.finished)

        self.health_check_state = HealthCheckState()

        def should_generate_more():
            # If we haven't found a bug, keep looking.  We check this before
            # doing anything else as it's by far the most common case.
            if not self.interesting_examples:
                return True
            # If we've found a bug and won't report more than one, stop looking.
            elif not self.settings.report_multiple_bugs:
                return False
            assert self.first_bug_found_at <= self.last_bug_found_at <= self.call_count
            # End the generation phase where we would have ended it if no bugs had
            # been found.  This reproduces the exit logic in `self.test_function`,
            # but with the important distinction that this clause will move on to
            # the shrinking phase having found one or more bugs, while the other
            # will exit having found zero bugs.
            if (
                self.valid_examples >= self.settings.max_examples
                or self.call_count >= max(self.settings.max_examples * 10, 1000)
            ):  # pragma: no cover
                return False
            # Otherwise, keep searching for between ten and 'a heuristic' calls.
            # We cap 'calls after first bug' so errors are reported reasonably
            # soon even for tests that are allowed to run for a very long time,
            # or sooner if the latest half of our test effort has been fruitless.
            return self.call_count < MIN_TEST_CALLS or self.call_count < min(
                self.first_bug_found_at + 1000, self.last_bug_found_at * 2
            )

        count = 0
        while should_generate_more() and (
            count < 10
            or self.health_check_state is not None
            # If we have not found a valid prefix yet, the target selector will
            # be empty and the mutation stage will fail with a very rare internal
            # error.  We therefore continue this initial random generation step
            # until we have found at least one prefix to mutate.
            or len(self.target_selector) == 0
        ):
            prefix = self.generate_novel_prefix()

            def draw_bytes(data, n):
                if data.index < len(prefix):
                    result = prefix[data.index : data.index + n]
                    # We always draw prefixes as a whole number of blocks
                    assert len(result) == n
                else:
                    result = uniform(self.random, n)
                return self.__zero_bound(data, result)

            last_data = self.new_conjecture_data(draw_bytes)
            self.test_function(last_data)
            last_data.freeze()

            count += 1

        mutations = 0
        mutator = self._new_mutator()

        zero_bound_queue = []

        while should_generate_more():
            if zero_bound_queue:
                # Whenever we generated an example and it hits a bound
                # which forces zero blocks into it, this creates a weird
                # distortion effect by making certain parts of the data
                # stream (especially ones to the right) much more likely
                # to be zero. We fix this by redistributing the generated
                # data by shuffling it randomly. This results in the
                # zero data being spread evenly throughout the buffer.
                # Hopefully the shrinking this causes will cause us to
                # naturally fail to hit the bound.
                # If it doesn't then we will queue the new version up again
                # (now with more zeros) and try again.
                overdrawn = zero_bound_queue.pop()
                buffer = bytearray(overdrawn.buffer)

                # These will have values written to them that are different
                # from what's in them anyway, so the value there doesn't
                # really "count" for distributional purposes, and if we
                # leave them in then they can cause the fraction of non
                # zero bytes to increase on redraw instead of decrease.
                for i in overdrawn.forced_indices:
                    buffer[i] = 0

                self.random.shuffle(buffer)
                buffer = hbytes(buffer)

                def draw_bytes(data, n):
                    result = buffer[data.index : data.index + n]
                    if len(result) < n:
                        result += hbytes(n - len(result))
                    return self.__rewrite(data, result)

                data = self.new_conjecture_data(draw_bytes=draw_bytes)
                self.test_function(data)
                data.freeze()
            else:
                origin = self.target_selector.select()
                mutations += 1
                data = self.new_conjecture_data(draw_bytes=mutator(origin))
                self.test_function(data)
                data.freeze()
                if data.status > origin.status:
                    mutations = 0
                elif data.status < origin.status or mutations >= 10:
                    # Cap the variations of a single example and move on to
                    # an entirely fresh start.  Ten is an entirely arbitrary
                    # constant, but it's been working well for years.
                    mutations = 0
                    mutator = self._new_mutator()
            if getattr(data, "hit_zero_bound", False):
                zero_bound_queue.append(data)
            mutations += 1