    def escape_local_minimum(self):
        """Attempt to restart the shrink process from a larger initial value in
        a way that allows us to escape a local minimum that the main greedy
        shrink process will get stuck in.

        The idea is that when we've completed the shrink process, we try
        starting it again from something reasonably near to the shrunk example
        that is likely to exhibit the same behaviour.

        We search for an example that is selected randomly among ones that are
        "structurally similar" to the original. If we don't find one we bail
        out fairly quickly as this will usually not work. If we do, we restart
        the shrink process from there. If this results in us finding a better
        final example, we do this again until it stops working.

        This is especially useful for things where the tendency to move
        complexity to the right works against us - often a generic instance of
        the problem is easy to shrink, but trying to reduce the size of a
        minimized example further is hard. For example suppose we had something
        like:

        x = data.draw(lists(integers()))
        y = data.draw(lists(integers(), min_size=len(x), max_size=len(x)))
        assert not (any(x) and any(y))

        Then this could shrink to something like [0, 1], [0, 1].

        Attempting to shrink this further by deleting an element of x would
        result in losing the last element of y, and the test would start
        passing. But if we were to replace this with [a, b], [c, d] with c != 0
        then deleting a or b would work.
        """
        count = 0
        while count < 10:
            count += 1
            self.debug('Retrying from random restart')
            attempt_buf = bytearray(self.shrink_target.buffer)

            # We use the shrinking information to identify the
            # structural locations in the byte stream - if lowering
            # the block would result in changing the size of the
            # example, changing it here is too likely to break whatever
            # it was caused the behaviour we're trying to shrink.
            # Everything non-structural, we redraw uniformly at random.
            for i, (u, v) in enumerate(self.blocks):
                if not self.is_shrinking_block(i):
                    attempt_buf[u:v] = uniform(self.__engine.random, v - u)
            attempt = self.cached_test_function(attempt_buf)
            if self.__predicate(attempt):
                prev = self.shrink_target
                self.update_shrink_target(attempt)
                self.__shrinking_block_cache = {}
                self.greedy_shrink()
                if (
                    sort_key(self.shrink_target.buffer) <
                    sort_key(prev.buffer)
                ):
                    # We have successfully shrunk the example past where
                    # we started from. Now we begin the whole process
                    # again from the new, smaller, example.
                    count = 0
                else:
                    self.update_shrink_target(prev)
                    self.__shrinking_block_cache = {}