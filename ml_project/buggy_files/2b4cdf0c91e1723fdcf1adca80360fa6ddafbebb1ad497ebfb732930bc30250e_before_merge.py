    def unique(self):
        return self._query_compiler.unique().to_numpy().squeeze()