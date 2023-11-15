    def __init__(self, slither: "SlitherCore"):
        super().__init__()
        self._scope: List[str] = []
        self._name: Optional[str] = None
        self._view: bool = False
        self._pure: bool = False
        self._payable: bool = False
        self._visibility: Optional[str] = None

        self._is_implemented: Optional[bool] = None
        self._is_empty: Optional[bool] = None
        self._entry_point: Optional["Node"] = None
        self._nodes: List["Node"] = []
        self._variables: Dict[str, "LocalVariable"] = {}
        # slithir Temporary and references variables (but not SSA)
        self._slithir_variables: Set["SlithIRVariable"] = set()
        self._parameters: List["LocalVariable"] = []
        self._parameters_ssa: List["LocalIRVariable"] = []
        self._parameters_src: Optional[SourceMapping] = None
        self._returns: List["LocalVariable"] = []
        self._returns_ssa: List["LocalIRVariable"] = []
        self._returns_src: Optional[SourceMapping] = None
        self._return_values: Optional[List["SlithIRVariable"]] = None
        self._return_values_ssa: Optional[List["SlithIRVariable"]] = None
        self._vars_read: List["Variable"] = []
        self._vars_written: List["Variable"] = []
        self._state_vars_read: List["StateVariable"] = []
        self._vars_read_or_written: List["Variable"] = []
        self._solidity_vars_read: List["SolidityVariable"] = []
        self._state_vars_written: List["StateVariable"] = []
        self._internal_calls: List["InternalCallType"] = []
        self._solidity_calls: List["SolidityFunction"] = []
        self._low_level_calls: List["LowLevelCallType"] = []
        self._high_level_calls: List["HighLevelCallType"] = []
        self._library_calls: List["LibraryCallType"] = []
        self._external_calls_as_expressions: List["Expression"] = []
        self._expression_vars_read: List["Expression"] = []
        self._expression_vars_written: List["Expression"] = []
        self._expression_calls: List["Expression"] = []
        # self._expression_modifiers: List["Expression"] = []
        self._modifiers: List[ModifierStatements] = []
        self._explicit_base_constructor_calls: List[ModifierStatements] = []
        self._contains_assembly: bool = False

        self._expressions: Optional[List["Expression"]] = None
        self._slithir_operations: Optional[List["Operation"]] = None
        self._slithir_ssa_operations: Optional[List["Operation"]] = None

        self._all_expressions: Optional[List["Expression"]] = None
        self._all_slithir_operations: Optional[List["Operation"]] = None
        self._all_internals_calls: Optional[List["InternalCallType"]] = None
        self._all_high_level_calls: Optional[List["HighLevelCallType"]] = None
        self._all_library_calls: Optional[List["LibraryCallType"]] = None
        self._all_low_level_calls: Optional[List["LowLevelCallType"]] = None
        self._all_solidity_calls: Optional[List["SolidityFunction"]] = None
        self._all_state_variables_read: Optional[List["StateVariable"]] = None
        self._all_solidity_variables_read: Optional[List["SolidityVariable"]] = None
        self._all_state_variables_written: Optional[List["StateVariable"]] = None
        self._all_slithir_variables: Optional[List["SlithIRVariable"]] = None
        self._all_nodes: Optional[List["Node"]] = None
        self._all_conditional_state_variables_read: Optional[List["StateVariable"]] = None
        self._all_conditional_state_variables_read_with_loop: Optional[List["StateVariable"]] = None
        self._all_conditional_solidity_variables_read: Optional[List["SolidityVariable"]] = None
        self._all_conditional_solidity_variables_read_with_loop: Optional[
            List["SolidityVariable"]
        ] = None
        self._all_solidity_variables_used_as_args: Optional[List["SolidityVariable"]] = None

        self._is_shadowed: bool = False
        self._shadows: bool = False

        # set(ReacheableNode)
        self._reachable_from_nodes: Set[ReacheableNode] = set()
        self._reachable_from_functions: Set[ReacheableNode] = set()

        # Constructor, fallback, State variable constructor
        self._function_type: Optional[FunctionType] = None
        self._is_constructor: Optional[bool] = None

        # Computed on the fly, can be True of False
        self._can_reenter: Optional[bool] = None
        self._can_send_eth: Optional[bool] = None

        self._nodes_ordered_dominators: Optional[List["Node"]] = None

        self._counter_nodes = 0

        # Memoize parameters:
        # TODO: identify all the memoize parameters and add a way to undo the memoization
        self._full_name: Optional[str] = None
        self._signature: Optional[Tuple[str, List[str], List[str]]] = None
        self._solidity_signature: Optional[str] = None
        self._signature_str: Optional[str] = None
        self._canonical_name: Optional[str] = None
        self._is_protected: Optional[bool] = None

        self._slither: "SlitherCore" = slither