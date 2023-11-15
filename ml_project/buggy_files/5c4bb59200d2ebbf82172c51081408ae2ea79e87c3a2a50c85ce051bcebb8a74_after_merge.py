    def analyze_typeddict_classdef(self, defn: ClassDef) -> bool:
        # special case for TypedDict
        possible = False
        for base_expr in defn.base_type_exprs:
            if isinstance(base_expr, RefExpr):
                base_expr.accept(self)
                if (base_expr.fullname == 'mypy_extensions.TypedDict' or
                        self.is_typeddict(base_expr)):
                    possible = True
        if possible:
            node = self.lookup(defn.name, defn)
            if node is not None:
                node.kind = GDEF  # TODO in process_namedtuple_definition also applies here
                if (len(defn.base_type_exprs) == 1 and
                        isinstance(defn.base_type_exprs[0], RefExpr) and
                        defn.base_type_exprs[0].fullname == 'mypy_extensions.TypedDict'):
                    # Building a new TypedDict
                    fields, types, required_keys = self.check_typeddict_classdef(defn)
                    info = self.build_typeddict_typeinfo(defn.name, fields, types, required_keys)
                    defn.info.replaced = info
                    node.node = info
                    defn.analyzed = TypedDictExpr(info)
                    defn.analyzed.line = defn.line
                    defn.analyzed.column = defn.column
                    return True
                # Extending/merging existing TypedDicts
                if any(not isinstance(expr, RefExpr) or
                       expr.fullname != 'mypy_extensions.TypedDict' and
                       not self.is_typeddict(expr) for expr in defn.base_type_exprs):
                    self.fail("All bases of a new TypedDict must be TypedDict types", defn)
                typeddict_bases = list(filter(self.is_typeddict, defn.base_type_exprs))
                keys = []  # type: List[str]
                types = []
                required_keys = set()
                for base in typeddict_bases:
                    assert isinstance(base, RefExpr)
                    assert isinstance(base.node, TypeInfo)
                    assert isinstance(base.node.typeddict_type, TypedDictType)
                    base_typed_dict = base.node.typeddict_type
                    base_items = base_typed_dict.items
                    valid_items = base_items.copy()
                    for key in base_items:
                        if key in keys:
                            self.fail('Cannot overwrite TypedDict field "{}" while merging'
                                      .format(key), defn)
                            valid_items.pop(key)
                    keys.extend(valid_items.keys())
                    types.extend(valid_items.values())
                    required_keys.update(base_typed_dict.required_keys)
                new_keys, new_types, new_required_keys = self.check_typeddict_classdef(defn, keys)
                keys.extend(new_keys)
                types.extend(new_types)
                required_keys.update(new_required_keys)
                info = self.build_typeddict_typeinfo(defn.name, keys, types, required_keys)
                defn.info.replaced = info
                node.node = info
                defn.analyzed = TypedDictExpr(info)
                defn.analyzed.line = defn.line
                defn.analyzed.column = defn.column
                return True
        return False