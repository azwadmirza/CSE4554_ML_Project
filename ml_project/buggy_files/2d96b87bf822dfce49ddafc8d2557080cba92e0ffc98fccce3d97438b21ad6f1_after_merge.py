    def render_Num(self, node):
        if isinstance(node.n, numbers.Integral):
            return sympy.Integer(node.n)
        else:
            return sympy.Float(node.n)