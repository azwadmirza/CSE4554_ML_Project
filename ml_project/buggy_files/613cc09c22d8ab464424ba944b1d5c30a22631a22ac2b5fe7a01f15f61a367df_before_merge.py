    def __init__(self, contract_name, lvalue):
        assert isinstance(contract_name, Constant)
        assert is_valid_lvalue(lvalue)
        super(NewContract, self).__init__()
        self._contract_name = contract_name
        # todo create analyze to add the contract instance
        self._lvalue = lvalue
        self._callid = None  # only used if gas/value != 0
        self._call_value = None