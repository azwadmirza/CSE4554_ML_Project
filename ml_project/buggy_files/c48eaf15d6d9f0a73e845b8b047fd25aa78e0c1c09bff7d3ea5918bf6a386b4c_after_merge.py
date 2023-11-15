    def _handle_Unop(self, expr):
        handler = None

        # All conversions are handled by the Conversion handler
        simop = vex_operations.get(expr.op)
        if simop is not None and simop.op_attrs['conversion']:
            handler = '_handle_Conversion'
        # Notice order of "Not" comparisons
        elif expr.op == 'Iop_Not1':
            handler = '_handle_Not1'
        elif expr.op.startswith('Iop_Not'):
            handler = '_handle_Not'

        if handler is not None and hasattr(self, handler):
            return getattr(self, handler)(expr)
        else:
            self.l.error('Unsupported Unop %s.', expr.op)
            return None