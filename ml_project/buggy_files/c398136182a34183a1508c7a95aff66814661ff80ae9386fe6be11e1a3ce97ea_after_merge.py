    def setup_class_def_analysis(self, defn: ClassDef) -> None:
        """Prepare for the analysis of a class definition."""
        if not defn.info:
            defn.info = TypeInfo(SymbolTable(), defn, self.cur_mod_id)
            defn.info._fullname = defn.info.name()
        if self.is_func_scope() or self.type:
            kind = MDEF
            if self.is_func_scope():
                kind = LDEF
            node = SymbolTableNode(kind, defn.info)
            self.add_symbol(defn.name, node, defn)
            if kind == LDEF:
                # We need to preserve local classes, let's store them
                # in globals under mangled unique names
                local_name = defn.info._fullname + '@' + str(defn.line)
                defn.info._fullname = self.cur_mod_id + '.' + local_name
                defn.fullname = defn.info._fullname
                self.globals[local_name] = node