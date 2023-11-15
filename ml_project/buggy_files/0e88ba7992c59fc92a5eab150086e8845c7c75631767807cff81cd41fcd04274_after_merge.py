    def visit_symbol_table(self, symtab: SymbolTable) -> None:
        # Copy the items because we may mutate symtab.
        for key, value in list(symtab.items()):
            cross_ref = value.cross_ref
            if cross_ref is not None:  # Fix up cross-reference.
                del value.cross_ref
                if cross_ref in self.modules:
                    value.node = self.modules[cross_ref]
                else:
                    stnode = lookup_qualified_stnode(self.modules, cross_ref,
                                                     self.quick_and_dirty)
                    if stnode is not None:
                        value.node = stnode.node
                        value.type_override = stnode.type_override
                    elif not self.quick_and_dirty:
                        assert stnode is not None, "Could not find cross-ref %s" % (cross_ref,)
                    else:
                        # We have a missing crossref in quick mode, need to put something
                        value.node = stale_info()
                        if value.kind == TYPE_ALIAS:
                            value.type_override = Instance(stale_info(), [])
            else:
                if isinstance(value.node, TypeInfo):
                    # TypeInfo has no accept().  TODO: Add it?
                    self.visit_type_info(value.node)
                elif value.node is not None:
                    value.node.accept(self)
                if value.type_override is not None:
                    value.type_override.accept(self.type_fixer)