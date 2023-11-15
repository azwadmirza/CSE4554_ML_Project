    def __init__(self, func_ir, parallel_options, swapped={}, typed=False):
        self.func_ir = func_ir
        self.parallel_options = parallel_options
        self.swapped = swapped
        self._processed_stencils = []
        self.typed = typed