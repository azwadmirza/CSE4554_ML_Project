    def __init__(self, contract_name, lvalue):
        super(TmpNewContract, self).__init__()
        self._contract_name = contract_name
        self._lvalue = lvalue
        self._call_value = None
        self._call_salt = None