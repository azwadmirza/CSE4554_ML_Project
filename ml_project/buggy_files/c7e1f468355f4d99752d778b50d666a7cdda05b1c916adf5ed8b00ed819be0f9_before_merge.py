    def __init__(
        self,
        function: Function,
        function_data: Dict,
        contract_parser: Optional["ContractSolc"],
        slither_parser: "SlitherSolc",
    ):
        self._slither_parser: "SlitherSolc" = slither_parser
        self._contract_parser = contract_parser
        self._function = function

        # Only present if compact AST
        self._referenced_declaration: Optional[int] = None
        if self.is_compact_ast:
            self._function.name = function_data["name"]
            if "id" in function_data:
                self._referenced_declaration = function_data["id"]
                self._function.id = function_data["id"]
        else:
            self._function.name = function_data["attributes"][self.get_key()]
        self._functionNotParsed = function_data
        self._params_was_analyzed = False
        self._content_was_analyzed = False

        self._counter_scope_local_variables = 0
        # variable renamed will map the solc id
        # to the variable. It only works for compact format
        # Later if an expression provides the referencedDeclaration attr
        # we can retrieve the variable
        # It only matters if two variables have the same name in the function
        # which is only possible with solc > 0.5
        self._variables_renamed: Dict[
            int, Union[LocalVariableSolc, LocalVariableInitFromTupleSolc]
        ] = {}

        self._analyze_type()

        self.parameters_src = SourceMapping()
        self.returns_src = SourceMapping()

        self._node_to_nodesolc: Dict[Node, NodeSolc] = dict()
        self._node_to_yulobject: Dict[Node, YulBlock] = dict()

        self._local_variables_parser: List[
            Union[LocalVariableSolc, LocalVariableInitFromTupleSolc]
        ] = []