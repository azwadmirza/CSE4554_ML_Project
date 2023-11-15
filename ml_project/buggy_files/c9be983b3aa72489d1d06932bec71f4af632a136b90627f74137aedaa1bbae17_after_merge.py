    def visit_unbound_type(self, t: UnboundType) -> Type:
        # TODO: replace with an assert after UnboundType can't leak from semantic analysis.
        return AnyType(TypeOfAny.from_error)