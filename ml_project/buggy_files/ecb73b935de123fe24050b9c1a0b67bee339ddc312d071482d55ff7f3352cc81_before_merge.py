    def add(self, name, parse_result):
        """Add the result to the parser cache.

        :param name:
        :type name: str
        :param parse_result:
        :type parse_result: ParseResult
        """
        self._previous_parsed[name] = parse_result
        while len(self._previous_parsed) > self._cache_size:
            del self._previous_parsed[self._previous_parsed.keys()[0]]