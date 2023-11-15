    def visit_member_expr(self, expr: MemberExpr) -> None:
        base = expr.expr
        base.accept(self)
        # Bind references to module attributes.
        if isinstance(base, RefExpr) and base.kind == MODULE_REF:
            # This branch handles the case foo.bar where foo is a module.
            # In this case base.node is the module's MypyFile and we look up
            # bar in its namespace.  This must be done for all types of bar.
            file = cast(MypyFile, base.node)
            n = file.names.get(expr.name, None) if file is not None else None
            if n:
                n = self.normalize_type_alias(n, expr)
                if not n:
                    return
                expr.kind = n.kind
                expr.fullname = n.fullname
                expr.node = n.node
            else:
                # We only catch some errors here; the rest will be
                # catched during type checking.
                #
                # This way we can report a larger number of errors in
                # one type checker run. If we reported errors here,
                # the build would terminate after semantic analysis
                # and we wouldn't be able to report any type errors.
                full_name = '%s.%s' % (file.fullname() if file is not None else None, expr.name)
                if full_name in obsolete_name_mapping:
                    self.fail("Module has no attribute %r (it's now called %r)" % (
                        expr.name, obsolete_name_mapping[full_name]), expr)
        elif isinstance(base, RefExpr) and isinstance(base.node, TypeInfo):
            # This branch handles the case C.bar where C is a class
            # and bar is a module resulting from `import bar` inside
            # class C.  Here base.node is a TypeInfo, and again we
            # look up the name in its namespace.  This is done only
            # when bar is a module; other things (e.g. methods)
            # are handled by other code in checkmember.
            n = base.node.names.get(expr.name)
            if n is not None and n.kind == MODULE_REF:
                n = self.normalize_type_alias(n, expr)
                if not n:
                    return
                expr.kind = n.kind
                expr.fullname = n.fullname
                expr.node = n.node