    def applies(cls, obj):
        return ((isinstance(obj, list) and all(cls.applies(o) for o in obj)) or
                hasattr(obj, 'to_plotly_json'))