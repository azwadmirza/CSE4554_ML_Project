    def perform_transform(self, node: Union[Node, SymbolTableNode],
                          transform: Callable[[Type], Type]) -> None:
        """Apply transform to all types associated with node."""
        if isinstance(node, ForStmt):
            if node.index_type:
                node.index_type = transform(node.index_type)
            self.transform_types_in_lvalue(node.index, transform)
        if isinstance(node, WithStmt):
            if node.target_type:
                node.target_type = transform(node.target_type)
            for n in node.target:
                if isinstance(n, NameExpr) and isinstance(n.node, Var) and n.node.type:
                    n.node.type = transform(n.node.type)
        if isinstance(node, (FuncDef, OverloadedFuncDef, CastExpr, AssignmentStmt,
                             TypeAliasExpr, Var)):
            assert node.type, "Scheduled patch for non-existent type"
            node.type = transform(node.type)
        if isinstance(node, NewTypeExpr):
            assert node.old_type, "Scheduled patch for non-existent type"
            node.old_type = transform(node.old_type)
            if node.info:
                new_bases = []  # type: List[Instance]
                for b in node.info.bases:
                    new_b = transform(b)
                    # TODO: this code can be combined with code in second pass.
                    if isinstance(new_b, Instance):
                        new_bases.append(new_b)
                    elif isinstance(new_b, TupleType):
                        new_bases.append(new_b.fallback)
                    else:
                        self.fail("Argument 2 to NewType(...) must be subclassable"
                                  " (got {})".format(new_b), node)
                        new_bases.append(self.builtin_type('object'))
                node.info.bases = new_bases
        if isinstance(node, TypeVarExpr):
            if node.upper_bound:
                node.upper_bound = transform(node.upper_bound)
            if node.values:
                node.values = [transform(v) for v in node.values]
        if isinstance(node, TypedDictExpr):
            assert node.info.typeddict_type, "Scheduled patch for non-existent type"
            node.info.typeddict_type = cast(TypedDictType,
                                            transform(node.info.typeddict_type))
        if isinstance(node, NamedTupleExpr):
            assert node.info.tuple_type, "Scheduled patch for non-existent type"
            node.info.tuple_type = cast(TupleType,
                                        transform(node.info.tuple_type))
        if isinstance(node, TypeApplication):
            node.types = [transform(t) for t in node.types]
        if isinstance(node, SymbolTableNode):
            assert node.type_override, "Scheduled patch for non-existent type"
            node.type_override = transform(node.type_override)
        if isinstance(node, TypeInfo):
            for tvar in node.defn.type_vars:
                if tvar.upper_bound:
                    tvar.upper_bound = transform(tvar.upper_bound)
                if tvar.values:
                    tvar.values = [transform(v) for v in tvar.values]
            new_bases = []
            for base in node.bases:
                new_base = transform(base)
                if isinstance(new_base, Instance):
                    new_bases.append(new_base)
                else:
                    # Don't fix the NamedTuple bases, they are Instance's intentionally.
                    # Patch the 'args' just in case, although generic tuple types are
                    # not supported yet.
                    alt_base = Instance(base.type, [transform(a) for a in base.args])
                    new_bases.append(alt_base)
            node.bases = new_bases