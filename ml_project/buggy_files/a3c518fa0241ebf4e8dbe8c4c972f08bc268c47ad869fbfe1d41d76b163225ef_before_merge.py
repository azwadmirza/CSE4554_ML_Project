    def __init__(self, function, contract):
        super(FunctionSolc, self).__init__()
        self._contract = contract
        if self.is_compact_ast:
            self._name = function['name']
        else:
            self._name = function['attributes'][self.get_key()]
        self._functionNotParsed = function
        self._params_was_analyzed = False
        self._content_was_analyzed = False
        self._counter_nodes = 0