    def visit_member_expr(self, expr: MemberExpr) -> None:
        base = expr.expr
        base.accept(self)
        # Bind references to module attributes.
        if isinstance(base, RefExpr) and base.kind == MODULE_REF:
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