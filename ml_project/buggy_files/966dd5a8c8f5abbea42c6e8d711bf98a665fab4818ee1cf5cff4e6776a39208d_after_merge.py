    def visit_import_all(self, i: ImportAll) -> None:
        i_id = self.correct_relative_import(i)
        if i_id in self.modules:
            m = self.modules[i_id]
            self.add_submodules_to_parent_modules(i_id, True)
            for name, node in m.names.items():
                node = self.normalize_type_alias(node, i)
                if not name.startswith('_') and node.module_public:
                    existing_symbol = self.globals.get(name)
                    if existing_symbol:
                        # Import can redefine a variable. They get special treatment.
                        if self.process_import_over_existing_name(
                                name, existing_symbol, node, i):
                            continue
                    self.add_symbol(name, SymbolTableNode(node.kind, node.node,
                                                          self.cur_mod_id,
                                                          node.type_override), i)
        else:
            # Don't add any dummy symbols for 'from x import *' if 'x' is unknown.
            pass