    def analyze_ordinary_member_access(self, e: MemberExpr,
                                       is_lvalue: bool) -> Type:
        """Analyse member expression or member lvalue."""
        if e.kind is not None:
            # This is a reference to a module attribute.
            return self.analyze_ref_expr(e)
        else:
            # This is a reference to a non-module attribute.
            original_type = self.accept(e.expr)
            member_type = analyze_member_access(
                e.name, original_type, e, is_lvalue, False, False,
                self.named_type, self.not_ready_callback, self.msg,
                original_type=original_type, chk=self.chk)
            if is_lvalue:
                return member_type
            else:
                return self.analyze_descriptor_access(original_type, member_type, e)