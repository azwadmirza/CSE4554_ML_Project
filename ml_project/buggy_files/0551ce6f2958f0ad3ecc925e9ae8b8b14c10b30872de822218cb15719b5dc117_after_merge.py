    def map(self, arg, na_action=None):
        if not callable(arg) and hasattr(arg, "get"):
            mapper = arg

            def arg(s):
                return mapper.get(s, np.nan)

        return self.__constructor__(
            query_compiler=self._query_compiler.applymap(
                lambda s: arg(s) if not pandas.isnull(s) or na_action is None else s
            )
        )