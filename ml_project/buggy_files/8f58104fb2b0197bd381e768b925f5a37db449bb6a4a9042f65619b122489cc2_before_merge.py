    def analyze_typevar_declaration(self, t: Type) -> List[Tuple[str, TypeVarExpr]]:
        if not isinstance(t, UnboundType):
            return None
        unbound = cast(UnboundType, t)
        sym = self.lookup_qualified(unbound.name, unbound)
        if sym is None:
            return None
        if sym.node.fullname() == 'typing.Generic':
            tvars = []  # type: List[Tuple[str, TypeVarExpr]]
            for arg in unbound.args:
                tvar = self.analyze_unbound_tvar(arg)
                if tvar:
                    tvars.append(tvar)
                else:
                    self.fail('Free type variable expected in %s[...]' %
                              sym.node.name(), t)
            return tvars
        return None