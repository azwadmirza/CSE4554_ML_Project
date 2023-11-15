    def _merge_cols_by_name(
        self,
        context,
        cursor_description,
        result_columns,
        loose_column_name_matching,
    ):
        dialect = context.dialect
        case_sensitive = dialect.case_sensitive
        match_map = self._create_description_match_map(
            result_columns, case_sensitive, loose_column_name_matching
        )

        for (
            idx,
            colname,
            untranslated,
            coltype,
        ) in self._colnames_from_description(context, cursor_description):
            try:
                ctx_rec = match_map[colname]
            except KeyError:
                mapped_type = sqltypes.NULLTYPE
                obj = None
            else:
                obj = ctx_rec[1]
                mapped_type = ctx_rec[2]
            yield idx, colname, mapped_type, coltype, obj, untranslated