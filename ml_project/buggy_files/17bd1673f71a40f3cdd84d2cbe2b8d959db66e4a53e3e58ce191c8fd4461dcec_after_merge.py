    def _adapt_to_context(self, context):
        """When using a cached Compiled construct that has a _result_map,
        for a new statement that used the cached Compiled, we need to ensure
        the keymap has the Column objects from our new statement as keys.
        So here we rewrite keymap with new entries for the new columns
        as matched to those of the cached statement.

        """

        if not context.compiled._result_columns:
            return self

        compiled_statement = context.compiled.statement
        invoked_statement = context.invoked_statement

        if compiled_statement is invoked_statement:
            return self

        # make a copy and add the columns from the invoked statement
        # to the result map.
        md = self.__class__.__new__(self.__class__)

        md._keymap = dict(self._keymap)

        keymap_by_position = self._keymap_by_result_column_idx

        for idx, new in enumerate(
            invoked_statement._exported_columns_iterator()
        ):
            try:
                rec = keymap_by_position[idx]
            except KeyError:
                # this can happen when there are bogus column entries
                # in a TextualSelect
                pass
            else:
                md._keymap[new] = rec

        md.case_sensitive = self.case_sensitive
        md._processors = self._processors
        assert not self._tuplefilter
        md._tuplefilter = None
        md._translated_indexes = None
        md._keys = self._keys
        md._keymap_by_result_column_idx = self._keymap_by_result_column_idx
        md._safe_for_cache = self._safe_for_cache
        return md