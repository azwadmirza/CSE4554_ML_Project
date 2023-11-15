    def add(self, name, parse_result):
        """Add the result to the parser cache.

        :param name:
        :type name: str
        :param parse_result:
        :type parse_result: ParseResult
        """
        with self.lock:
            while len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            self.cache[name] = parse_result