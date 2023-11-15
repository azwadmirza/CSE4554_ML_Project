    def add_symbol(self, name: str, node: SymbolTableNode,
                   context: Context) -> None:
        # NOTE: This logic mostly parallels SemanticAnalyzerPass1.add_symbol. If you change
        #     this, you may have to change the other method as well.
        if self.is_func_scope():
            assert self.locals[-1] is not None
            if name in self.locals[-1]:
                # Flag redefinition unless this is a reimport of a module.
                if not (node.kind == MODULE_REF and
                        self.locals[-1][name].node == node.node):
                    self.name_already_defined(name, context, self.locals[-1][name])
            self.locals[-1][name] = node
        elif self.type:
            self.type.names[name] = node
        else:
            existing = self.globals.get(name)
            if (existing
                    and (not isinstance(node.node, MypyFile) or existing.node != node.node)
                    and existing.kind != UNBOUND_IMPORTED
                    and not isinstance(existing.node, ImportedName)):
                # Modules can be imported multiple times to support import
                # of multiple submodules of a package (e.g. a.x and a.y).
                ok = False
                # Only report an error if the symbol collision provides a different type.
                if existing.type and node.type and is_same_type(existing.type, node.type):
                    ok = True
                if not ok:
                    self.name_already_defined(name, context, existing)
            self.globals[name] = node