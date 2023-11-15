    def __init__(self, parent, cursor_description):
        context = parent.context
        dialect = context.dialect
        self._tuplefilter = None
        self._translated_indexes = None
        self.case_sensitive = dialect.case_sensitive
        self._safe_for_cache = False

        if context.result_column_struct:
            (
                result_columns,
                cols_are_ordered,
                textual_ordered,
                loose_column_name_matching,
            ) = context.result_column_struct
            num_ctx_cols = len(result_columns)
        else:
            result_columns = (
                cols_are_ordered
            ) = (
                num_ctx_cols
            ) = loose_column_name_matching = textual_ordered = False

        # merge cursor.description with the column info
        # present in the compiled structure, if any
        raw = self._merge_cursor_description(
            context,
            cursor_description,
            result_columns,
            num_ctx_cols,
            cols_are_ordered,
            textual_ordered,
            loose_column_name_matching,
        )

        self._keymap = {}

        # processors in key order for certain per-row
        # views like __iter__ and slices
        self._processors = [
            metadata_entry[MD_PROCESSOR] for metadata_entry in raw
        ]

        # keymap by primary string...
        by_key = dict(
            [
                (metadata_entry[MD_LOOKUP_KEY], metadata_entry)
                for metadata_entry in raw
            ]
        )

        # for compiled SQL constructs, copy additional lookup keys into
        # the key lookup map, such as Column objects, labels,
        # column keys and other names
        if num_ctx_cols:

            # if by-primary-string dictionary smaller (or bigger?!) than
            # number of columns, assume we have dupes, rewrite
            # dupe records with "None" for index which results in
            # ambiguous column exception when accessed.
            if len(by_key) != num_ctx_cols:
                # new in 1.4: get the complete set of all possible keys,
                # strings, objects, whatever, that are dupes across two
                # different records, first.
                index_by_key = {}
                dupes = set()
                for metadata_entry in raw:
                    for key in (metadata_entry[MD_RENDERED_NAME],) + (
                        metadata_entry[MD_OBJECTS] or ()
                    ):
                        if not self.case_sensitive and isinstance(
                            key, util.string_types
                        ):
                            key = key.lower()
                        idx = metadata_entry[MD_INDEX]
                        # if this key has been associated with more than one
                        # positional index, it's a dupe
                        if index_by_key.setdefault(key, idx) != idx:
                            dupes.add(key)

                # then put everything we have into the keymap excluding only
                # those keys that are dupes.
                self._keymap.update(
                    [
                        (obj_elem, metadata_entry)
                        for metadata_entry in raw
                        if metadata_entry[MD_OBJECTS]
                        for obj_elem in metadata_entry[MD_OBJECTS]
                        if obj_elem not in dupes
                    ]
                )

                # then for the dupe keys, put the "ambiguous column"
                # record into by_key.
                by_key.update({key: (None, (), key) for key in dupes})

            else:
                # no dupes - copy secondary elements from compiled
                # columns into self._keymap
                self._keymap.update(
                    [
                        (obj_elem, metadata_entry)
                        for metadata_entry in raw
                        if metadata_entry[MD_OBJECTS]
                        for obj_elem in metadata_entry[MD_OBJECTS]
                    ]
                )

        # update keymap with primary string names taking
        # precedence
        self._keymap.update(by_key)

        # update keymap with "translated" names (sqlite-only thing)
        if not num_ctx_cols and context._translate_colname:
            self._keymap.update(
                [
                    (
                        metadata_entry[MD_UNTRANSLATED],
                        self._keymap[metadata_entry[MD_LOOKUP_KEY]],
                    )
                    for metadata_entry in raw
                    if metadata_entry[MD_UNTRANSLATED]
                ]
            )