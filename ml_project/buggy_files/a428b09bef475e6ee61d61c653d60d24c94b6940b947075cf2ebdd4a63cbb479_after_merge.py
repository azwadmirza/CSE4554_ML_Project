    def params_for_label(instruction):
        """Get the params and format them to add them to a label. None if there are no params."""
        if not hasattr(instruction.op, 'params'):
            return None
        ret = []
        for param in instruction.op.params:
            if isinstance(param, (sympy.Number, float)):
                ret.append('%.5g' % param)
            else:
                ret.append('%s' % param)
        return ret