    def __init__(self, values):
        # Note: Can return None 
        # ex: return call()
        # where call() dont return
        if not isinstance(values, list):
            assert is_valid_rvalue(values) or isinstance(values, TupleVariable) or values is None
            if values is None:
                values = []
            else:
                values = [values]
        else:
            # Remove None
            # Prior Solidity 0.5
            # return (0,)
            # was valid for returns(uint)
            values = [v for v in values if not v is None]
            self._valid_value(values)
        super(Return, self).__init__()
        self._values = values