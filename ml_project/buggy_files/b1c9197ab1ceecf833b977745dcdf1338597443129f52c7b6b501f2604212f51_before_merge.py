    async def _get_statement(self, query, timeout, *, named: bool=False):
        statement = self._stmt_cache.get(query)
        if statement is not None:
            return statement

        # Only use the cache when:
        #  * `statement_cache_size` is greater than 0;
        #  * query size is less than `max_cacheable_statement_size`.
        use_cache = self._stmt_cache.get_max_size() > 0
        if (use_cache and
                self._config.max_cacheable_statement_size and
                len(query) > self._config.max_cacheable_statement_size):
            use_cache = False

        if use_cache or named:
            stmt_name = self._get_unique_id('stmt')
        else:
            stmt_name = ''

        statement = await self._protocol.prepare(stmt_name, query, timeout)

        ready = statement._init_types()
        if ready is not True:
            if self._types_stmt is None:
                self._types_stmt = await self.prepare(self._intro_query)

            types = await self._types_stmt.fetch(list(ready))
            self._protocol.get_settings().register_data_types(types)

        if use_cache:
            self._stmt_cache.put(query, statement)

        # If we've just created a new statement object, check if there
        # are any statements for GC.
        if self._stmts_to_close:
            await self._cleanup_stmts()

        return statement