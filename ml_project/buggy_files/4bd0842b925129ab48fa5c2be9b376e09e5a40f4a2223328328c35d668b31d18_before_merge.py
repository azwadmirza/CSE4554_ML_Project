    def visit_erased_type(self, left: ErasedType) -> bool:
        # Should not get here.
        raise RuntimeError()