    def unique(self):
        return self.__constructor__(
            query_compiler=self._query_compiler.unique()
        ).to_numpy()