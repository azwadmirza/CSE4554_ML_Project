    def analyze_namedtuple_classdef(self, defn: ClassDef) -> bool:
        # special case for NamedTuple
        for base_expr in defn.base_type_exprs:
            if isinstance(base_expr, RefExpr):
                base_expr.accept(self)
                if base_expr.fullname == 'typing.NamedTuple':
                    node = self.lookup(defn.name, defn)
                    if node is not None:
                        node.kind = GDEF  # TODO in process_namedtuple_definition also applies here
                        items, types, default_items = self.check_namedtuple_classdef(defn)
                        node.node = self.build_namedtuple_typeinfo(
                            defn.name, items, types, default_items)
                        return True
        return False