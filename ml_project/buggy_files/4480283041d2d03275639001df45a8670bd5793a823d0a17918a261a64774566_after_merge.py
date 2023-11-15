    def parse(self, name, cache_result=True):
        """Parse the name into a ParseResult.

        :param name:
        :type name: str
        :param cache_result:
        :type cache_result: bool
        :return:
        :rtype: ParseResult
        """
        name = helpers.unicodify(name)

        if self.naming_pattern:
            cache_result = False

        cached = name_parser_cache.get(name)
        if cached:
            return cached

        result = self._parse_string(name)
        self.assert_supported(result)

        if cache_result:
            name_parser_cache.add(name, result)

        logger.debug('Parsed {name} into {result}', name=name, result=str(result))
        return result