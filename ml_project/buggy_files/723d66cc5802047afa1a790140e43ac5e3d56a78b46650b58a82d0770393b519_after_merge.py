    def __init__(self, operators: List[str], operands: List[Expression]) -> None:
        self.operators = operators
        self.operands = operands
        self.method_types = []
        self.literal = min(o.literal for o in self.operands)
        self.literal_hash = ((cast(Any, 'Comparison'),) + tuple(operators) +
                             tuple(o.literal_hash for o in operands))