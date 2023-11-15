    def visit_erased_type(self, left: ErasedType) -> bool:
        # We can get here when isinstance is used inside a lambda
        # whose type is being inferred. In any event, we have no reason
        # to think that an ErasedType will end up being the same as
        # any other type, even another ErasedType.
        return False