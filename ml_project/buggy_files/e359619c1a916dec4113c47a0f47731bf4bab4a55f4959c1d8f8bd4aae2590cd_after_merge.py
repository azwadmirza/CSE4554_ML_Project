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
                        # We only really need the assignments in the body to be type checked later;
                        # attempting to type check methods may lead to crashes because NamedTuples
                        # do not have a fully functional TypeInfo.
                        # TODO remove this hack and add full support for NamedTuple methods
                        defn.defs.body = [stmt for stmt in defn.defs.body
                                          if isinstance(stmt, AssignmentStmt)]
                        return True
        return False