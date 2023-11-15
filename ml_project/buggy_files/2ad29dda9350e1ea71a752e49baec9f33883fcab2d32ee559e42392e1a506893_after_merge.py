    def __init__(self, subdir, lineno, colno, condition, trueblock, falseblock):
        self.subdir = subdir
        self.lineno = lineno
        self.colno = colno
        self.condition = condition
        self.trueblock = trueblock
        self.falseblock = falseblock