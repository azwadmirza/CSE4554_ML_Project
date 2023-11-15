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

        self._counter_scope_local_variables = 0
        # variable renamed will map the solc id
        # to the variable. It only works for compact format
        # Later if an expression provides the referencedDeclaration attr
        # we can retrieve the variable
        # It only matters if two variables have the same name in the function
        # which is only possible with solc > 0.5
        self._variables_renamed = {}