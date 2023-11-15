    def lookup(self, name: str, ctx: Context) -> SymbolTableNode:
        """Look up an unqualified name in all active namespaces."""
        # 1a. Name declared using 'global x' takes precedence
        if name in self.global_decls[-1]:
            if name in self.globals:
                return self.globals[name]
            else:
                self.name_not_defined(name, ctx)
                return None
        # 1b. Name declared using 'nonlocal x' takes precedence
        if name in self.nonlocal_decls[-1]:
            for table in reversed(self.locals[:-1]):
                if table is not None and name in table:
                    return table[name]
            else:
                self.name_not_defined(name, ctx)
                return None
        # 2. Class attributes (if within class definition)
        if self.is_class_scope() and name in self.type.names:
            return self.type.names[name]
        # 3. Local (function) scopes
        for table in reversed(self.locals):
            if table is not None and name in table:
                return table[name]
        # 4. Current file global scope
        if name in self.globals:
            return self.globals[name]
        # 5. Builtins
        b = self.globals.get('__builtins__', None)
        if b:
            table = cast(MypyFile, b.node).names
            if name in table:
                if name[0] == "_" and name[1] != "_":
                    self.name_not_defined(name, ctx)
                    return None
                node = table[name]
                return node
        # Give up.
        self.name_not_defined(name, ctx)
        self.check_for_obsolete_short_name(name, ctx)
        return None