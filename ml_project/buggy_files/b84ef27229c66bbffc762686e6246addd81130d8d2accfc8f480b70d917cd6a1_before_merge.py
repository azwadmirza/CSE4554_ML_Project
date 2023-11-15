    def get_declaration(self, node: Node) -> Type:
        if isinstance(node, (RefExpr, SymbolTableNode)) and isinstance(node.node, Var):
            type = node.node.type
            if isinstance(type, PartialType):
                return None
            return type
        else:
            return None