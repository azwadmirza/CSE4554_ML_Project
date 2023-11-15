    def __setstate__(self, state):
        self._processors = [None for _ in range(len(state["_keys"]))]
        self._keymap = state["_keymap"]

        self._keymap_by_result_column_idx = {
            rec[MD_RESULT_MAP_INDEX]: rec for rec in self._keymap.values()
        }
        self._keys = state["_keys"]
        self.case_sensitive = state["case_sensitive"]

        if state["_translated_indexes"]:
            self._translated_indexes = state["_translated_indexes"]
            self._tuplefilter = tuplegetter(*self._translated_indexes)
        else:
            self._translated_indexes = self._tuplefilter = None