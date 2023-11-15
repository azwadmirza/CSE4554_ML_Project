    def setup_class_def_analysis(self, defn: ClassDef) -> None:
        """Prepare for the analysis of a class definition."""
        if not defn.info:
            defn.info = TypeInfo(SymbolTable(), defn, self.cur_mod_id)
            defn.info._fullname = defn.info.name()
        if self.is_func_scope() or self.type:
            kind = MDEF
            if self.is_func_scope():
                kind = LDEF
            self.add_symbol(defn.name, SymbolTableNode(kind, defn.info), defn)