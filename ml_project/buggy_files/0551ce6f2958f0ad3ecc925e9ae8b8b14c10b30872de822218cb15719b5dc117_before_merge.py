    def map(self, arg, na_action=None):
        return self.__constructor__(query_compiler=self._query_compiler.applymap(arg))