    def extend(self, iterable):
        # Empty iterable, do nothing
        if len(iterable) == 0:
            return self
        if not self._typed:
            # Need to get the first element of the iterable to initialise the
            # type of the list. FIXME: this may be a problem if the iterable
            # can not be sliced.
            self._initialise_list(iterable[0])
        return _extend(self, iterable)