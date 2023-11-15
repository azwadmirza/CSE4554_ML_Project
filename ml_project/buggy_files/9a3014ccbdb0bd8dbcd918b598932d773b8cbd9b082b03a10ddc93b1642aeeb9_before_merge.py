    def visit_file(self, file_node: MypyFile, fnam: str, options: Options,
                   patches: List[Callable[[], None]]) -> None:
        """Run semantic analysis phase 2 over a file.

        Add callbacks by mutating the patches list argument. They will be called
        after all semantic analysis phases but before type checking.
        """
        self.recurse_into_functions = True
        self.options = options
        self.errors.set_file(fnam, file_node.fullname())
        self.cur_mod_node = file_node
        self.cur_mod_id = file_node.fullname()
        self.is_stub_file = fnam.lower().endswith('.pyi')
        self.is_typeshed_stub_file = self.errors.is_typeshed_file(file_node.path)
        self.globals = file_node.names
        self.patches = patches

        with experiments.strict_optional_set(options.strict_optional):
            if 'builtins' in self.modules:
                self.globals['__builtins__'] = SymbolTableNode(MODULE_REF,
                                                               self.modules['builtins'])

            for name in implicit_module_attrs:
                v = self.globals[name].node
                if isinstance(v, Var):
                    assert v.type is not None, "Type of implicit attribute not set"
                    v.type = self.anal_type(v.type)
                    v.is_ready = True

            defs = file_node.defs
            for d in defs:
                self.accept(d)

            if self.cur_mod_id == 'builtins':
                remove_imported_names_from_symtable(self.globals, 'builtins')
                for alias_name in type_aliases:
                    self.globals.pop(alias_name.split('.')[-1], None)

            if '__all__' in self.globals:
                for name, g in self.globals.items():
                    if name not in self.all_exports:
                        g.module_public = False

            del self.options
            del self.patches