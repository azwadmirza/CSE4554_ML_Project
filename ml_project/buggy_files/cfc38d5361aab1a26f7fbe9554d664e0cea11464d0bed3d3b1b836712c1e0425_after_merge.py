    def __getstate__(self):
        return {
            "_keymap": {
                key: (rec[MD_INDEX], rec[MD_RESULT_MAP_INDEX], _UNPICKLED, key)
                for key, rec in self._keymap.items()
                if isinstance(key, util.string_types + util.int_types)
            },
            "_keys": self._keys,
            "case_sensitive": self.case_sensitive,
            "_translated_indexes": self._translated_indexes,
            "_tuplefilter": self._tuplefilter,
        }