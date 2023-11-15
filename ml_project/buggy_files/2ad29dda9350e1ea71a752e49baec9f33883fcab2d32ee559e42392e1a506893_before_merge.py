    def __init__(self, lineno, colno, condition, trueblock, falseblock):
        self.lineno = lineno
        self.colno = colno
        self.condition = condition
        self.trueblock = trueblock
        self.falseblock = falseblock