    def get_declaration(self, expr: Node) -> Type:
        if isinstance(expr, RefExpr) and isinstance(expr.node, Var):
            type = expr.node.type
            if isinstance(type, PartialType):
                return None
            return type
        else:
            return None