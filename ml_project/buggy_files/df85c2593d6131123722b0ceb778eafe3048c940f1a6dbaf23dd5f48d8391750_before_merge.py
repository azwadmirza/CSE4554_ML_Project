    def __init__(self, called, nbr_arguments, result, type_call):
        assert isinstance(called, (Contract,
                                   Variable,
                                   SolidityVariableComposed,
                                   SolidityFunction,
                                   Structure,
                                   Event))
        super(TmpCall, self).__init__()
        self._called = called
        self._nbr_arguments = nbr_arguments
        self._type_call = type_call
        self._lvalue = result
        self._ori = None # 
        self._callid = None
        self._gas = None
        self._value = None