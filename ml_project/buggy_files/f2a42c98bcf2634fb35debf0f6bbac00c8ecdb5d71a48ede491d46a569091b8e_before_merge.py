    def extend(self, iterable):
        if not self._typed:
            # Need to get the first element of the iterable to initialise the
            # type of the list. FIXME: this may be a problem if the iterable
            # can not be sliced.
            self._initialise_list(iterable[0])
            self.append(iterable[0])
            return _extend(self, iterable[1:])
        return _extend(self, iterable)