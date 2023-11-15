        def keyfunc(obj):
            """Uses bitwidth to order numeric-types.
            Fallback to hash() for arbitary ordering.
            """
            return getattr(obj, 'bitwidth', hash(obj))