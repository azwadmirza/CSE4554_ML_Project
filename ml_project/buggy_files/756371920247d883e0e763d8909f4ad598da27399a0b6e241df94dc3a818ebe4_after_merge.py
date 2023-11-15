        def keyfunc(obj):
            """Uses bitwidth to order numeric-types.
            Fallback to stable, deterministic sort.
            """
            return getattr(obj, 'bitwidth', 0)