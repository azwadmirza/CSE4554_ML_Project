    def add_symbol(self, name: str, node: SymbolTableNode,
                   context: Context) -> None:
        # NOTE: This is closely related to SemanticAnalyzerPass2.add_symbol. Since both methods
        #     will be called on top-level definitions, they need to co-operate. If you change
        #     this, you may have to change the other method as well.
        if self.sem.is_func_scope():
            assert self.sem.locals[-1] is not None
            if name in self.sem.locals[-1]:
                # Flag redefinition unless this is a reimport of a module.
                if not (node.kind == MODULE_REF and
                        self.sem.locals[-1][name].node == node.node):
                    self.sem.name_already_defined(name, context, self.sem.locals[-1][name])
            self.sem.locals[-1][name] = node
        else:
            assert self.sem.type is None  # Pass 1 doesn't look inside classes
            existing = self.sem.globals.get(name)
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
                    self.sem.name_already_defined(name, context, existing)
            elif not existing:
                self.sem.globals[name] = node