    def __init__(self, local_variable):
        assert isinstance(local_variable, LocalVariable)

        super(LocalIRVariable, self).__init__()

        # initiate ChildContract
        self.set_function(local_variable.function)

        # initiate Variable
        self._name = local_variable.name
        self._initial_expression = local_variable.expression
        self._type = local_variable.type
        self._initialized = local_variable.initialized
        self._visibility = local_variable.visibility
        self._is_constant = local_variable.is_constant

        # initiate LocalVariable
        self._location = self.location
        self._is_storage = self.is_storage

        self._index = 0

        # Additional field
        # points to state variables
        self._refers_to = set()

        # keep un-ssa version
        if isinstance(local_variable, LocalIRVariable):
            self._non_ssa_version = local_variable.non_ssa_version
        else:
            self._non_ssa_version = local_variable
        self._non_ssa_version = local_variable