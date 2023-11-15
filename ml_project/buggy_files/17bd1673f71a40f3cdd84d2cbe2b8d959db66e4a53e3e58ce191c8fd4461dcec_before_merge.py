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

        # match up new columns positionally to the result columns
        for existing, new in zip(
            context.compiled._result_columns,
            invoked_statement._exported_columns_iterator(),
        ):
            if existing[RM_NAME] in md._keymap:
                md._keymap[new] = md._keymap[existing[RM_NAME]]

        md.case_sensitive = self.case_sensitive
        md._processors = self._processors
        assert not self._tuplefilter
        md._tuplefilter = None
        md._translated_indexes = None
        md._keys = self._keys
        return md