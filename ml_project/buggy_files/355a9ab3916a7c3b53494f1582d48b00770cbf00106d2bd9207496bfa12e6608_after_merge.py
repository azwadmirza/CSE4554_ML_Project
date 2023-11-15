    def get(self, name):
        """Return the cached parsed result.

        :param name:
        :type name: str
        :return:
        :rtype: ParseResult
        """
        with self.lock:
            if name in self.cache:
                log.debug('Using cached parse result for {name}', {'name': name})
                return self.cache[name]