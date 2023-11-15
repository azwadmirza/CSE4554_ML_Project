    def __init__(self, template, funcptr, cconv=None):
        self.funcptr = funcptr
        self.cconv = cconv
        super(FunctionPointer, self).__init__(template)