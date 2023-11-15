    def _merge_cols_by_none(self, context, cursor_description):
        for (
            idx,
            colname,
            untranslated,
            coltype,
        ) in self._colnames_from_description(context, cursor_description):
            yield (
                idx,
                None,
                colname,
                sqltypes.NULLTYPE,
                coltype,
                None,
                untranslated,
            )