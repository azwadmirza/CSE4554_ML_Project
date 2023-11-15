    def _is_supported_npycall(self, expr):
        """check if we support parfor translation for
        this Numpy call.
        """
        #return False # turn off for now
        if not (isinstance(expr, ir.Expr) and expr.op == 'call'):
            return False
        if expr.func.name not in self.array_analysis.numpy_calls.keys():
            return False
        call_name = self.array_analysis.numpy_calls[expr.func.name]
        if call_name in ['zeros', 'ones', 'random.ranf']:
            return True
        # TODO: add more calls
        if call_name=='dot':
            #only translate matrix/vector and vector/vector multiply to parfor
            # (don't translate matrix/matrix multiply)
            if (self._get_ndims(expr.args[0].name)<=2 and
                    self._get_ndims(expr.args[1].name)==1):
                return True
        return False