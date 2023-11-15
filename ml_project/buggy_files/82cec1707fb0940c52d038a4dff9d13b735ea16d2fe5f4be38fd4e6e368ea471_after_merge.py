    def __init__(self, contract_name):
        super(NewContract, self).__init__()
        self._contract_name = contract_name
        self._gas = None
        self._value = None
        self._salt = None