    def analyze_namedtuple_classdef(self, defn: ClassDef) -> Optional[TypeInfo]:
        # special case for NamedTuple
        for base_expr in defn.base_type_exprs:
            if isinstance(base_expr, RefExpr):
                base_expr.accept(self)
                if base_expr.fullname == 'typing.NamedTuple':
                    node = self.lookup(defn.name, defn)
                    if node is not None:
                        node.kind = GDEF  # TODO in process_namedtuple_definition also applies here
                        items, types, default_items = self.check_namedtuple_classdef(defn)
                        info = self.build_namedtuple_typeinfo(
                            defn.name, items, types, default_items)
                        node.node = info
                        defn.info.replaced = info
                        defn.info = info
                        defn.analyzed = NamedTupleExpr(info)
                        defn.analyzed.line = defn.line
                        defn.analyzed.column = defn.column
                        return info
        return None