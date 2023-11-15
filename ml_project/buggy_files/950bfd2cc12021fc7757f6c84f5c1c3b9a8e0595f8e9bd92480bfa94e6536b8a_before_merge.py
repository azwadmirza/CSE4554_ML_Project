    def get(self, name):
        """Return the cached parsed result.

        :param name:
        :type name: str
        :return:
        :rtype: ParseResult
        """
        if name in self._previous_parsed:
            logger.debug("Using cached parse result for '{name}'", name=name)
            return self._previous_parsed[name]