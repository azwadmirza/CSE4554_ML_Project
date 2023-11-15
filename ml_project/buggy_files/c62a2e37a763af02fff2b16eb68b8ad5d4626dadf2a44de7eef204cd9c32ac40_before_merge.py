    def create_from_context() -> Optional["_XlaDistModel"]:
        if not has_xla_support:
            return None
        return _XlaDistModel()